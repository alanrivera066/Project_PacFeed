# Tabla de decisiones del pipeline — PacFeed

## Lógica de veredicto

El pipeline corre 4 etapas en secuencia. Si **cualquiera** falla, el veredicto es **BLOQUEA**. Solo si las 4 pasan el veredicto es **PERMITE**.

---

## Etapas

### Etapa 1 — Secretos (gitleaks)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | gitleaks |
| **Umbral** | Cero hallazgos — cualquier secreto detectado bloquea |
| **Riesgo concreto de PacFeed** | El `.env` contiene las credenciales de RDS y las claves temporales de AWS Academy. Si alguien sube accidentalmente el `.env` al repo, cualquiera con acceso puede vaciar la base de datos o gastar el presupuesto del lab. |
| **Por qué este umbral** | Un secreto filtrado no tiene "severidad media" — o está o no está. Umbral de cero es el único que tiene sentido. |

---

### Etapa 2 — IaC (checkov)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | checkov |
| **Umbral** | Cero hallazgos HIGH o CRITICAL en las reglas seleccionadas |
| **Riesgo concreto de PacFeed** | El `.tf` define el bucket S3 y el RDS. Si el bucket queda con acceso público, las fotos de perfil son visibles para cualquiera. Si el RDS queda sin cifrado o con acceso público, los datos de usuarios (usernames, hashes) quedan expuestos. |
| **Por qué este umbral** | Los requisitos del PDF exigen explícitamente: bucket privado, RDS sin acceso público y cifrado. Un hallazgocritíco en IaC significa que el código contradice ese requisito. |
| **Reglas checkov aplicadas** | CKV_AWS_18 (S3 logging), CKV_AWS_19 (S3 cifrado), CKV_AWS_20 (S3 público), CKV_AWS_54 (S3 acceso público bloqueado), CKV_AWS_145 (S3 KMS), CKV_AWS_293 (RDS acceso público), CKV2_AWS_6 (S3 block public) |

---

### Etapa 3 — SAST (bandit)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | bandit |
| **Umbral** | Cero hallazgos de severidad HIGH con confianza HIGH (`-ll -ii`) |
| **Riesgo concreto de PacFeed** | PacFeed recibe input del usuario (contenido de posts, usernames). Bandit detecta si en alguna versión futura alguien usa `execute()` con interpolación de strings en vez de parámetros, o usa `eval()` con input del usuario — vulnerabilidades que en una red social permiten borrar datos de otros usuarios. |
| **Por qué este umbral** | `-ll -ii` filtra solo HIGH/HIGH para no bloquear por advertencias de baja severidad que no representan riesgo real en este contexto académico. |

---

### Etapa 4 — Dependencias (pip-audit)

| Campo | Detalle |
|-------|---------|
| **Herramienta** | pip-audit |
| **Umbral** | Cero CVE con severidad HIGH o CRITICAL |
| **Riesgo concreto de PacFeed** | Flask, psycopg2 y boto3 son las librerías con más superficie de ataque. Una CVE crítica en Flask puede permitir ejecución remota o bypass de autenticación. Una CVE en psycopg2 puede exponer los datos de RDS. |
| **Por qué este umbral** | CVE HIGH/CRITICAL tienen exploit conocido o probable. CVE de severidad MEDIUM o LOW generalmente requieren condiciones específicas que no aplican a este proyecto académico. |

---

## Qué decidí NO cubrir (y por qué)

| Control no incluido | Razón |
|--------------------|-------|
| **Análisis de imagen Docker** (trivy/grype) | Agrega complejidad al pipeline y en el lab las imágenes vienen de Docker Hub oficial — el riesgo real es bajo para un proyecto académico. |
| **DAST** (análisis dinámico) | Requiere la app corriendo durante el pipeline. El valor para esta app simple no justifica la complejidad de levantarla en CI. |
| **Cobertura de tests** | No hay tests unitarios — la rúbrica no los pide explícitamente para Avance 2. |
| **Licencias de dependencias** | No hay restricciones de licenciamiento en un proyecto académico. |
