"""
Funcionalidad: buscar publicaciones por nombre de usuario
Tema: Red social de formato corto

REMEDIACION aplicada (CWE-89 - SQL Injection):
  - Se reemplazo la concatenacion de strings por consulta parametrizada.
  - psycopg2 escapa automaticamente el valor del parametro antes de enviarlo
    a PostgreSQL, eliminando la posibilidad de inyeccion SQL.
  - Se agrego validacion de longitud maxima para descartar entradas invalidas.
"""
from flask import Blueprint, request, jsonify
import os
import psycopg2

buscar_bp = Blueprint("buscar", __name__)

# Longitud maxima permitida para el nombre de usuario
MAX_USUARIO_LEN = 50


def obtener_conexion():
    # Reutiliza la conexion configurada hacia RDS.
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


@buscar_bp.route("/publicaciones/buscar", methods=["GET"])
def buscar_por_usuario():
    """Devuelve las publicaciones de un usuario dado su nombre."""
    nombre_usuario = request.args.get("usuario", "").strip()

    # Validacion de entrada - descarta valores vacios o demasiado largos
    if not nombre_usuario:
        return jsonify({"error": "El parametro 'usuario' es requerido"}), 400

    if len(nombre_usuario) > MAX_USUARIO_LEN:
        return jsonify({"error": f"El nombre de usuario no puede superar {MAX_USUARIO_LEN} caracteres"}), 400

    # REMEDIACION: consulta parametrizada - el valor nunca se interpola
    # directamente en el string SQL. psycopg2 lo envia como dato separado.
    # Se busca en la tabla 'posts' uniendo con 'users' para filtrar por el
    # nombre de usuario (username), que es el esquema real de la aplicacion.
    consulta = (
        "SELECT p.id, p.contenido, p.created_at "
        "FROM posts p "
        "JOIN users u ON p.user_id = u.id "
        "WHERE u.username = %s "
        "ORDER BY p.created_at DESC LIMIT 20"
    )

    conexion = obtener_conexion()
    cur = conexion.cursor()
    cur.execute(consulta, (nombre_usuario,))  # parametro seguro
    rows = cur.fetchall()
    cur.close()
    conexion.close()

    publicaciones = [
        {"id": r[0], "contenido": r[1], "fecha_creacion": str(r[2])}
        for r in rows
    ]

    return jsonify({"usuario": nombre_usuario, "publicaciones": publicaciones})
