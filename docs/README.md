# PacFeed

Red social de formato corto. Publicaciones breves, seguir usuarios, dar like y ver el feed de a quién sigues.

## Cómo se levanta

### Requisitos
- Docker y docker-compose instalados en la EC2
- Archivo `.env` con las variables de entorno (ver `.env.example`)

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url-repo>
cd pacfeed

# 2. Crear el .env
cp .env.example .env
# Editar .env con los valores reales

# 3. Levantar
docker compose up -d

# 4. Verificar
curl http://localhost:5000/salud
```

## Interfaz web

La aplicación incluye un frontend simple servido por Flask en la raíz (`/`).
Permite registrarse, iniciar sesión, publicar, ver el feed, seguir usuarios y
buscar publicaciones por nombre de usuario. Abre `http://<host>:5000/` en el
navegador.

## Pipeline CI/CD

El repositorio incluye un pipeline en **GitHub Actions**
(`.github/workflows/pipeline.yml`) que corre en cada push: cuatro etapas de
seguridad (gitleaks, checkov, bandit, pip-audit), build de la imagen Docker y
deploy automático por SSH a la instancia de QA. Ver `docs/tabla_decisiones_pipeline.md`
para el detalle de cada control.

## Servicios de AWS

| Servicio | Uso |
|----------|-----|
| EC2 (t3.small, Amazon Linux 2023) | Corre docker-compose con la API y Redis |
| RDS PostgreSQL 15 (db.t3.micro) | Base de datos principal — cifrada, sin acceso público |
| S3 | Almacén de fotos de perfil — privado, cifrado, acceso público bloqueado |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/salud` | Health check |
| POST | `/registro` | Crear cuenta |
| POST | `/login` | Iniciar sesión (devuelve user_id) |
| POST | `/posts` | Publicar texto (header: X-User-Id) |
| GET | `/feed` | Feed de seguidos (header: X-User-Id) |
| POST | `/follow/<id>` | Seguir usuario (header: X-User-Id) |
| POST | `/like/<post_id>` | Dar like (header: X-User-Id) |
| POST | `/perfil/foto` | Subir foto a S3 (header: X-User-Id) |
| GET | `/publicaciones/buscar?usuario=...` | Buscar publicaciones por nombre de usuario |
| GET | `/` | Interfaz web (frontend) |

## Autenticación

Simple por header: después de `/login` usa el `user_id` devuelto como header `X-User-Id` en las rutas protegidas.

## Redis / caché

El feed se guarda en Redis con TTL de 5 minutos. Se invalida automáticamente cuando alguien a quien sigues publica algo nuevo.
