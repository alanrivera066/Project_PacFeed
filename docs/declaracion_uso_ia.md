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

---

# Declaración de uso de IA — Entrega Final (De QA a Producción)

## Qué hice con IA

- Integré el parche de la funcionalidad nueva (`app/buscar_publicaciones.py` —
  búsqueda de publicaciones por usuario) con ayuda de Kiro (IA), adaptando la
  conexión a la base de datos al mismo `psycopg2` que ya usa la aplicación.
- Usé IA para analizar el parche e identificar la falla de seguridad que traía
  escondida: una inyección SQL (CWE-89) por concatenación directa del parámetro
  `usuario` en la consulta.
- Remedié la falla con ayuda de IA, reemplazando la concatenación por una
  consulta parametrizada y agregando validación de entrada.
- Migré el pipeline de un script bash local a GitHub Actions con ayuda de IA,
  conservando las cuatro etapas de seguridad del Avance 2 (gitleaks, checkov,
  bandit, pip-audit) y agregando build de la imagen Docker y deploy por SSH.
- Generé el frontend web (`app/templates/index.html`) con ayuda de IA.
- Redacté los documentos de esta entrega (`clasificacion_hallazgo.md`,
  `respuesta_incidente.md`, `evidencia_produccion.md`) usando IA como punto de
  partida.

## Qué revisé, decidí y ajusté yo

- Decidí migrar el pipeline **completo** a GitHub Actions (conservando las cuatro
  etapas de seguridad) en lugar de dejar solo un análisis mínimo, para no perder
  los controles que ya tenía del Avance 2.
- Verifiqué en la práctica que el pipeline detuviera el parche vulnerable: revisé
  la corrida en rojo y confirmé que el hallazgo bloqueado era efectivamente la
  inyección SQL (B608 / CWE-89) y no otro control.
- Ajusté el umbral de confianza de bandit a `low` tras comprobar que la inyección
  SQL se reportaba con confianza baja y no bloqueaba con la configuración anterior.
- Identifiqué y documenté como falso positivo justificado el hallazgo B104
  (bind a `0.0.0.0`), por ser intencional dentro del contenedor.
- Configuré los secrets del repositorio (host, usuario y llave SSH) y creé el
  archivo `.env` en las instancias, verificando que nunca se sube al repositorio.
- Creé la instancia de Producción y validé el despliegue del código ya remediado.
