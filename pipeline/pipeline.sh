#!/usr/bin/env bash
# PacFeed — Pipeline de seguridad
# Veredicto único: BLOQUEA si cualquier etapa falla, PERMITE si todas pasan.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=1
resultado_global=$PASS

log()  { echo "[INFO]  $*"; }
error(){ echo "[ERROR] $*"; }
ok()   { echo "[OK]    $*"; }

separador() { echo ""; echo "======================================"; echo "  $*"; echo "======================================"; }

# ---------------------------------------------------------------------------
# Etapa 1 — Secretos (gitleaks)
# ---------------------------------------------------------------------------
separador "ETAPA 1: Secretos — gitleaks"
if ! command -v gitleaks &>/dev/null; then
  error "gitleaks no encontrado. Instala: https://github.com/gitleaks/gitleaks"
  resultado_global=$FAIL
else
  if gitleaks detect --source "$REPO_ROOT" --no-git --redact 2>&1; then
    ok "Etapa 1 PASA — sin secretos detectados"
  else
    error "Etapa 1 FALLA — secretos detectados"
    resultado_global=$FAIL
  fi
fi

# ---------------------------------------------------------------------------
# Etapa 2 — IaC (checkov)
# ---------------------------------------------------------------------------
separador "ETAPA 2: IaC — checkov"
if ! command -v checkov &>/dev/null; then
  error "checkov no encontrado. Instala: pip install checkov"
  resultado_global=$FAIL
else
  if checkov -d "$REPO_ROOT/infra" \
      --framework terraform \
      --check CKV_AWS_20,CKV_AWS_54,CKV2_AWS_6,CKV_AWS_19 \
      --compact 2>&1; then
    ok "Etapa 2 PASA — sin hallazgos HIGH/CRITICAL en IaC"
  else
    error "Etapa 2 FALLA — hallazgos HIGH/CRITICAL en IaC"
    resultado_global=$FAIL
  fi
fi

# ---------------------------------------------------------------------------
# Etapa 3 — SAST (bandit)
# ---------------------------------------------------------------------------
separador "ETAPA 3: SAST — bandit"
if ! command -v bandit &>/dev/null; then
  error "bandit no encontrado. Instala: pip install bandit"
  resultado_global=$FAIL
else
  if bandit -r "$REPO_ROOT/app" -ll -ii 2>&1; then
    ok "Etapa 3 PASA — sin hallazgos HIGH en el código"
  else
    error "Etapa 3 FALLA — hallazgos HIGH en el código"
    resultado_global=$FAIL
  fi
fi

# ---------------------------------------------------------------------------
# Etapa 4 — Dependencias (pip-audit)
# ---------------------------------------------------------------------------
separador "ETAPA 4: Dependencias — pip-audit"
if ! command -v pip-audit &>/dev/null; then
  error "pip-audit no encontrado. Instala: pip install pip-audit"
  resultado_global=$FAIL
else
  if pip-audit -r "$REPO_ROOT/app/requirements.txt" 2>&1; then
    ok "Etapa 4 PASA — sin CVE HIGH/CRITICAL en dependencias"
  else
    error "Etapa 4 FALLA — CVE HIGH/CRITICAL en dependencias"
    resultado_global=$FAIL
  fi
fi

# ---------------------------------------------------------------------------
# Veredicto final
# ---------------------------------------------------------------------------
separador "VEREDICTO FINAL"
if [ "$resultado_global" -eq "$PASS" ]; then
  echo ""
  echo "  ✅  PERMITE — todas las etapas pasaron"
  echo ""
  exit 0
else
  echo ""
  echo "  ❌  BLOQUEA — una o más etapas fallaron (ver arriba)"
  echo ""
  exit 1
fi
