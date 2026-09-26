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

### Pipeline: GitHub Actions (no script bash ni Jenkins)

Para la Entrega Final el pipeline se migró a GitHub Actions. En el Avance 2 se
había usado un script bash local (`pipeline/pipeline.sh`) para generar las
corridas roja y verde; ese script se conserva en el repositorio como referencia
histórica, pero el pipeline que realmente controla los despliegues ahora vive en
`.github/workflows/pipeline.yml` y se dispara automáticamente en cada push.

Se eligió GitHub Actions sobre Jenkins porque no requiere levantar ni mantener un
servidor aparte (Jenkins consumiría recursos del Learner Lab), se integra directo
con el repositorio y ejecuta las mismas cuatro etapas de seguridad del bash
original —gitleaks, checkov, bandit y pip-audit— más las etapas de build de la
imagen Docker y despliegue por SSH a la instancia de QA.

**Descartado:** Jenkins (requiere servidor dedicado), script bash como pipeline
principal (no se dispara solo ni bloquea despliegues de forma automática).

---

### Ambientes: dos repositorios separados (QA/Desarrollo y Producción)

Para la Entrega Final se separaron los ambientes en dos repositorios distintos:

- **QA / Desarrollo** (`Project_PacFeed`): es donde se aplica el parche, corre el
  pipeline completo con deploy automático a la instancia de QA, se detecta la
  falla y se remedia. Aquí vive todo el historial del trabajo, incluidos los
  commits del parche vulnerable y su corrección.
- **Producción** (`Project_PacFeed_Prod`): repositorio nuevo que nace con el
  código ya remediado y validado en verde. Su pipeline corre las cuatro etapas
  de seguridad y el build, pero **no** hace deploy automático — el despliegue a
  la instancia de Producción es manual y controlado. A este repo nunca llega el
  parche vulnerable.

Se eligió esta separación para reflejar un flujo real de promoción de código: QA
es el ambiente de trabajo y validación, y a Producción solo se promueve lo que ya
pasó los controles. Mantener repos separados deja una frontera clara entre "lo que
se está probando" y "lo que está en producción".

**Descartado:** un solo repositorio con ramas (más simple, pero no separa tan
claramente los dos ambientes para fines de la entrega).
