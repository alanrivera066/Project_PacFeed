import os
import hashlib
import json
import boto3
import psycopg2
import redis
from flask import Flask, request, jsonify, g
from functools import wraps

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Conexiones
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
    return g.db


def get_redis():
    if "redis" not in g:
        g.redis = redis.Redis(
            host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True,
        )
    return g.redis


def get_s3():
    return boto3.client(
        "s3",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# Inicializar tablas
# ---------------------------------------------------------------------------

def init_db():
    db = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            foto_s3_key VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            contenido VARCHAR(280) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS follows (
            id SERIAL PRIMARY KEY,
            follower_id INTEGER REFERENCES users(id),
            followed_id INTEGER REFERENCES users(id),
            UNIQUE(follower_id, followed_id)
        );
        CREATE TABLE IF NOT EXISTS likes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            post_id INTEGER REFERENCES posts(id),
            UNIQUE(user_id, post_id)
        );
    """)
    db.commit()
    cur.close()
    db.close()


# ---------------------------------------------------------------------------
# Auth simple: header X-User-Id
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.headers.get("X-User-Id")
        if not user_id:
            return jsonify({"error": "Se requiere X-User-Id"}), 401
        g.user_id = int(user_id)
        return f(*args, **kwargs)
    return decorated


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.route("/salud")
def salud():
    return jsonify({"estado": "ok"}), 200


@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "username y password requeridos"}), 400

    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
            (username, hash_password(password)),
        )
        user_id = cur.fetchone()[0]
        db.commit()
    except psycopg2.errors.UniqueViolation:
        db.rollback()
        return jsonify({"error": "username ya existe"}), 409
    finally:
        cur.close()
    return jsonify({"user_id": user_id, "username": username}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id FROM users WHERE username=%s AND password_hash=%s",
        (username, hash_password(password)),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        return jsonify({"error": "credenciales inválidas"}), 401
    return jsonify({"user_id": row[0]}), 200


@app.route("/posts", methods=["POST"])
@login_required
def crear_post():
    data = request.get_json()
    contenido = data.get("contenido", "").strip()
    if not contenido:
        return jsonify({"error": "contenido requerido"}), 400
    if len(contenido) > 280:
        return jsonify({"error": "máximo 280 caracteres"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO posts (user_id, contenido) VALUES (%s, %s) RETURNING id",
        (g.user_id, contenido),
    )
    post_id = cur.fetchone()[0]
    db.commit()
    cur.close()

    # Invalidar caché del feed de todos los seguidores
    r = get_redis()
    cur2 = get_db().cursor()
    cur2.execute("SELECT follower_id FROM follows WHERE followed_id=%s", (g.user_id,))
    followers = cur2.fetchall()
    cur2.close()
    for (follower_id,) in followers:
        r.delete(f"feed:{follower_id}")

    return jsonify({"post_id": post_id}), 201


@app.route("/feed", methods=["GET"])
@login_required
def feed():
    r = get_redis()
    cache_key = f"feed:{g.user_id}"
    cached = r.get(cache_key)
    if cached:
        return jsonify({"feed": json.loads(cached), "from_cache": True}), 200

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT p.id, p.contenido, p.created_at, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id IN (
            SELECT followed_id FROM follows WHERE follower_id = %s
        )
        ORDER BY p.created_at DESC
        LIMIT 50
    """, (g.user_id,))
    rows = cur.fetchall()
    cur.close()

    result = [
        {"post_id": r[0], "contenido": r[1], "created_at": str(r[2]), "username": r[3]}
        for r in rows
    ]
    # Guardar en caché 5 minutos
    r2 = get_redis()
    r2.setex(cache_key, 300, json.dumps(result))

    return jsonify({"feed": result, "from_cache": False}), 200


@app.route("/follow/<int:followed_id>", methods=["POST"])
@login_required
def follow(followed_id):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO follows (follower_id, followed_id) VALUES (%s, %s)",
            (g.user_id, followed_id),
        )
        db.commit()
    except psycopg2.errors.UniqueViolation:
        db.rollback()
        return jsonify({"error": "ya sigues a este usuario"}), 409
    finally:
        cur.close()
    # Invalidar mi propio feed
    get_redis().delete(f"feed:{g.user_id}")
    return jsonify({"ok": True}), 200


@app.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like(post_id):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO likes (user_id, post_id) VALUES (%s, %s)",
            (g.user_id, post_id),
        )
        db.commit()
    except psycopg2.errors.UniqueViolation:
        db.rollback()
        return jsonify({"error": "ya diste like"}), 409
    finally:
        cur.close()
    return jsonify({"ok": True}), 200


@app.route("/perfil/foto", methods=["POST"])
@login_required
def subir_foto():
    if "foto" not in request.files:
        return jsonify({"error": "archivo 'foto' requerido"}), 400
    foto = request.files["foto"]
    bucket = os.environ["S3_BUCKET"]
    key = f"fotos/{g.user_id}/{foto.filename}"

    s3 = get_s3()
    s3.upload_fileobj(foto, bucket, key)

    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET foto_s3_key=%s WHERE id=%s", (key, g.user_id))
    db.commit()
    cur.close()
    return jsonify({"s3_key": key}), 200


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
