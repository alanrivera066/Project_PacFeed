# Tabla de decisiones del pipeline — PacFeed

## Lógica de veredicto

El pipeline corre 4 etapas en secuencia. Si cualquiera falla, el veredicto es BLOQUEA. Solo si las 4 pasan el veredicto es PERMITE. Esto es así porque cada control cubre una posible brecha de seguridad que se tiene que arreglar de inmediato antes de comprometer la seguridad u operatividad de la aplicación.

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
| **Umbral** | Cero hallazgos de severidad HIGH con confianza HIGH |
| **Riesgo concreto de PacFeed** | Bandit ayuda a detectar si no se está limitando correctamente la entrada de datos del usuario. Si no se controla, un atacante podría realizar ataques de inyección SQL a través del contenido de los posts o el username. |
| **Por qué este umbral** | Se filtran solo hallazgos HIGH/HIGH para no bloquear por advertencias de baja severidad que no representan un riesgo real en este contexto. |

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
