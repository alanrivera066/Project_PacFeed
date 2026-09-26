# Tabla de decisiones del pipeline — PacFeed

## Dónde corre

El pipeline está implementado en **GitHub Actions** (`.github/workflows/pipeline.yml`)
y se dispara automáticamente en cada push a `main`. Las cuatro etapas de seguridad
descritas abajo se ejecutan como jobs independientes; si cualquiera falla, el deploy
queda bloqueado.

## Lógica de veredicto

El pipeline corre 4 etapas de seguridad. Si cualquiera falla, el veredicto es BLOQUEA y no se despliega. Solo si las 4 pasan continúa a las etapas de build (imagen Docker) y deploy (SSH a la instancia de QA) — el veredicto PERMITE. Esto es así porque cada control cubre una posible brecha de seguridad que se tiene que arreglar de inmediato antes de comprometer la seguridad u operatividad de la aplicación.

---

## Etapas

### Etapa 1 — Secretos (gitleaks)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | gitleaks |
| **Umbral** | Cero hallazgos — cualquier secreto detectado bloquea |
| **Riesgo concreto de PacFeed** | Si un atacante tuviera acceso al repositorio, se encontraría con las credenciales en texto plano, lo que le daría acceso a la base de datos para usarla con fines maliciosos. |
| **Por qué este umbral** | Un secreto no puede ser "menos importante" que otro. Las credenciales dan acceso a los recursos más importantes de la aplicación, por lo que el umbral es cero sin excepciones. |

---

### Etapa 2 — IaC (checkov)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | checkov |
| **Umbral** | Cero hallazgos HIGH o CRITICAL en las reglas seleccionadas |
| **Riesgo concreto de PacFeed** | Checkov detecta malas configuraciones en el archivo `.tf`. Por ejemplo, si la base de datos tuviera acceso desde internet, cualquiera podría ver la información de los usuarios de PacFeed. |
| **Por qué este umbral** | Un hallazgo crítico en IaC significa que el código contradice directamente los requisitos de seguridad: bucket privado y RDS sin acceso público. |
| **Reglas aplicadas** | CKV_AWS_19 (S3 cifrado), CKV_AWS_20 (S3 sin ACL pública), CKV_AWS_54 (S3 block public policy), CKV2_AWS_6 (S3 block public access) |

---

### Etapa 3 — SAST (bandit)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | bandit |
| **Umbral** | Bloquea con hallazgos de severidad MEDIUM o superior (cualquier nivel de confianza) |
| **Riesgo concreto de PacFeed** | Bandit ayuda a detectar si no se está limitando correctamente la entrada de datos del usuario. Si no se controla, un atacante podría realizar ataques de inyección SQL a través del contenido de los posts o el username. |
| **Por qué este umbral** | El parche de la funcionalidad de búsqueda introdujo una inyección SQL (B608, CWE-89) que Bandit reporta con severidad MEDIUM y confianza *Low*. Para no dejarla pasar, el umbral de confianza se bajó a `low`, de modo que cualquier hallazgo MEDIUM o superior bloquee el despliegue. Este ajuste fue clave para que el pipeline detuviera el parche vulnerable en la Entrega Final. |

---

### Etapa 4 — Dependencias (pip-audit)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | pip-audit |
| **Umbral** | Cero CVE con severidad HIGH o CRITICAL |
| **Riesgo concreto de PacFeed** | Verifica si alguna librería como Flask o psycopg2 tiene una vulnerabilidad conocida. Si existe una, ya habría una brecha de seguridad que un atacante podría explotar como backdoor para comprometer la aplicación. |
| **Por qué este umbral** | CVE HIGH o CRITICAL tienen exploit conocido o probable. Los de severidad menor generalmente requieren condiciones muy específicas que no aplican a este proyecto. |

---

## Qué decidí NO cubrir y por qué

| Control no incluido | Razón |
|--------------------|-------|
| **Análisis de imagen Docker (trivy)** | Docker Hub tiene un proceso de revisión en las imágenes oficiales, por lo que el riesgo real para este proyecto es bajo. |
| **DAST (pruebas dinámicas)** | Requiere tener infraestructura extra levantada solo para las pruebas, lo cual no es necesario para este avance. |

---

## Etapas de entrega (build y deploy)

Cuando las 4 etapas de seguridad pasan, el pipeline continúa con dos etapas de entrega:

| Etapa | Qué hace |
|-------|----------|
| **Build (Docker)** | Construye la imagen de la aplicación con el `Dockerfile` para verificar que el código empaqueta correctamente antes de desplegar. |
| **Deploy a QA** | Se conecta por SSH a la instancia EC2 de QA, actualiza el código (`git pull`), reconstruye los contenedores con `docker compose` y verifica el health check en `/salud`. Solo corre en push a `main`. |

La promoción a **Producción** se hace de forma manual y controlada: solo se despliega en la instancia de Producción el código que ya pasó el pipeline completo en verde. El parche vulnerable nunca llega a Producción.
