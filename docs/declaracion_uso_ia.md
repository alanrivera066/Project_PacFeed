# Declaración de uso de IA — PacFeed

## Qué hice con IA

- Generé la estructura inicial del código de `app/app.py` con ayuda de Kiro (IA).
- Generé el `Dockerfile`, `docker-compose.yml`, `infra/main.tf` y `pipeline/pipeline.sh` con ayuda de IA.
- Generé los documentos de `docs/` con ayuda de IA como punto de partida.

## Qué revisé y corregí yo

- Verifiqué que los endpoints corresponden con el modelo de datos que decidí.
- Confirmé que el Security Group de RDS referencia al SG de la EC2 (no CIDR abierto).
- Ajusté las herramientas del pipeline (gitleaks, checkov) a las que ya conocía del curso.
- Revisé que el `.env.example` no contiene credenciales reales y que `.env` está en `.gitignore`.
- Verifiqué la tabla de decisiones contra los requisitos reales del PDF de la rúbrica.

## Compromisos

Entiendo el código que entrego y puedo justificar cada decisión técnica si se me pregunta en la calificación.
