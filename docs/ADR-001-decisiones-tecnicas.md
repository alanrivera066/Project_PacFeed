# ADR-001 — Decisiones técnicas de PacFeed

## Contexto

Proyecto académico individual (LSCA2314). El objetivo es cumplir los requisitos mínimos de la rúbrica con la implementación más simple posible.

## Decisiones

### Backend: Flask (no FastAPI)

Se utilizó Flask para mantener el proyecto simple. FastAPI tiene beneficios como generación automática de documentación, pero agrega complejidad que no aporta valor para un proyecto de este tamaño.

**Descartado:** FastAPI.

---

### Base de datos: psycopg2 directo (no ORM)

Se utilizó psycopg2 porque la aplicación solo tiene cuatro tablas simples. SQLAlchemy, a pesar de sus beneficios como generar SQL automáticamente, no aporta mucho valor a un proyecto de este calibre.

**Descartado:** SQLAlchemy.

---

### Autenticación: X-User-Id en header (no JWT)

Para el inicio de sesión no se utilizó otra manera más que después del login el servidor devuelva un user_id para que el cliente lo agregue en cada petición. Se maneja de esta manera para mantenerlo simple y sin tanta complejidad.

**Descartado:** JWT, Flask-Login, sesiones con cookies.

---

### Caché: Redis con invalidación simple

Redis corre en su propio contenedor separado de la API. Cuando alguien pide su feed, la app primero revisa si está en Redis — si está lo devuelve directo (from_cache: true), si no está va a RDS y guarda el resultado en Redis para la próxima vez. El caché se invalida cuando alguien a quien sigues publica algo nuevo. Esta estrategia cumple con el requisito de que se note que sirve desde caché cuando puede, sin necesidad de ser sofisticado.

---

### Orquestación: docker-compose (no Kubernetes)

Se decidió utilizar docker-compose por la memoria limitada que tiene la instancia dentro del Learner Lab. Kubernetes es opcional en la rúbrica y arriesgar la entrega por un punto extra no vale la pena.

**Descartado:** Kubernetes (k3s, minikube).

---

### IaC: Terraform (no CloudFormation)

Terraform es la herramienta usada en el curso y tiene mejor soporte en el pipeline con checkov.

**Descartado:** CloudFormation.

---

### Pipeline: script bash (no Jenkins ni GitHub Actions)

Se decidió utilizar un script bash para generar las corridas roja y verde y posteriormente guardarlas en la carpeta de reportes, antes que instalar Jenkins u otro servidor para manejar el pipeline. Se mantiene la simplicidad sin necesidad de infraestructura adicional.

**Descartado:** Jenkins, GitHub Actions.
