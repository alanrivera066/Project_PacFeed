# ADR-001 — Decisiones técnicas de PacFeed

## Contexto

Proyecto académico individual (LSCA2314). El objetivo es cumplir los requisitos mínimos de la rúbrica con la implementación más simple posible.

## Decisiones

### Backend: Flask (no FastAPI)

**Elegido porque:** Flask es más simple para un proyecto pequeño sin schemas complejos. No necesitamos validación automática de tipos ni documentación OpenAPI autogenerada — eso agregaría complejidad sin valor para la rúbrica.

**Descartado:** FastAPI — más potente pero más boilerplate para lo que necesitamos.

### Base de datos: psycopg2 directo (no ORM)

**Elegido porque:** Son 4 tablas simples. Un ORM (SQLAlchemy) agregaría una capa de abstracción innecesaria y más dependencias.

**Descartado:** SQLAlchemy, tortoise-orm.

### Autenticación: X-User-Id en header (no JWT)

**Elegido porque:** La rúbrica pide "registro e inicio de sesión simples — no necesita ser sofisticado". JWT agrega complejidad (expiración, refresh tokens, firma) que no aporta puntos.

**Descartado:** JWT, Flask-Login, sesiones con cookies.

### Contraseñas: SHA-256 (no bcrypt)

**Elegido porque:** Es un proyecto académico en un entorno de lab. bcrypt sería mejor para producción, pero agrega una dependencia extra.

**Nota:** En producción real se usaría bcrypt o argon2.

### Caché: Redis con invalidación simple

**Elegido porque:** La pieza técnica obligatoria del tema 2 es Redis. La invalidación se hace borrando la clave del feed cuando hay contenido nuevo — simple y funcional.

**Descartado:** Invalidación por TTL únicamente (no demuestra que el caché sirve el feed), estrategias de write-through (más complejo).

### Orquestación: docker-compose (no Kubernetes)

**Elegido porque:** La rúbrica dice explícitamente que docker-compose es el piso obligatorio y Kubernetes es opcional y arriesgado por memoria. No se arriesga la entrega por un bono.

### IaC: Terraform (no CloudFormation)

**Elegido porque:** Terraform es la herramienta usada en el curso y tiene mejor soporte en el pipeline con checkov.

### Pipeline: script bash (no Jenkins ni GitHub Actions)

**Elegido porque:** Para correr el pipeline manualmente en la EC2 y generar las corridas roja y verde, un script bash es suficiente y no requiere configurar infraestructura adicional.
