# Declaración de uso de IA — PacFeed

## Qué hice con IA

- Generé la estructura inicial del código de `app/app.py` con ayuda de Kiro (IA). El uso de IA para escribir código de la aplicación es una práctica recomendada en el curso.
- Generé el `Dockerfile`, `docker-compose.yml`, `infra/main.tf` y `pipeline/pipeline.sh` con ayuda de IA.
- Generé los documentos de `docs/` con ayuda de IA como punto de partida.

## Qué revisé y ajusté yo

- Seleccioné las herramientas del pipeline (gitleaks, checkov, bandit, pip-audit) basándome en las vistas en el curso.
- Ajusté los umbrales de cada etapa del pipeline según los riesgos concretos de PacFeed.
- Verifiqué que el Security Group de RDS referencia al SG de la EC2 y no un CIDR abierto.
- Confirmé que el `.env` no está en el repositorio y que `.gitignore` lo excluye correctamente.
- Resolví los problemas de compatibilidad de herramientas en el entorno del Learner Lab (versiones de Python, flags de pip-audit, configuración de gitleaks).
- Revisé la tabla de decisiones del pipeline contra los requisitos reales del PDF de la rúbrica.

## Sobre el entendimiento del proyecto

El uso de IA para generar código de la aplicación es explícitamente recomendado en el curso. Mi responsabilidad es entender las decisiones de diseño, las herramientas de seguridad utilizadas y poder justificar cada etapa del pipeline — que es el foco de evaluación del Avance 2.
