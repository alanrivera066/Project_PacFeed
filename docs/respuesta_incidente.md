# Respuesta al Incidente de Seguridad

**Proyecto:** PacFeed — Red social de formato corto  
**Falla:** SQL Injection en `GET /publicaciones/buscar` (CWE-89)  
**Fecha:** Pipeline de QA bloqueado — ver `reportes/pipeline_bloqueado.*`

---

## Contención inmediata

> Lo que se haría AHORA MISMO para frenar el riesgo mientras se prepara el
> arreglo real. No corrige la causa raíz, solo detiene el sangrado.

### Acción: Deshabilitar el endpoint con una bandera de entorno

Se agrega la variable de entorno `BUSCAR_HABILITADO=false` en el archivo `.env`
y se modifica el endpoint para que retorne `503` cuando la bandera está apagada:

```python
import os
from flask import Blueprint, request, jsonify

buscar_bp = Blueprint("buscar", __name__)

@buscar_bp.route("/publicaciones/buscar", methods=["GET"])
def buscar_por_usuario():
    if os.environ.get("BUSCAR_HABILITADO", "true").lower() != "true":
        return jsonify({"error": "Funcionalidad temporalmente deshabilitada"}), 503
    # ... resto del código
```

**Pasos para aplicar la contención:**

1. Agregar `BUSCAR_HABILITADO=false` al archivo `.env` en la instancia QA.
2. Reiniciar el contenedor: `docker compose restart api`
3. Verificar que el endpoint devuelve 503: `curl http://localhost:5000/publicaciones/buscar?usuario=test`
4. El endpoint queda bloqueado para usuarios reales mientras se trabaja en el fix.

**Lo que esto NO resuelve:** La causa raíz (concatenación SQL insegura) sigue
en el código. Si alguien reactiva la bandera sin remediar el código, la
vulnerabilidad vuelve a estar activa.

---

## Prevención

> El arreglo real en el código que elimina la causa raíz, para que esa clase
> de falla no vuelva a ocurrir. Es lo que efectivamente sube a Producción.

### Acción: Reemplazar concatenación de strings por consulta parametrizada

La corrección elimina por completo la construcción manual del string SQL y
utiliza el mecanismo de parámetros de `psycopg2`, que escapa automáticamente
cualquier valor ingresado por el usuario:

**Código vulnerable (antes):**
```python
consulta = (
    "SELECT id, contenido, fecha_creacion FROM publicaciones "
    "WHERE usuario = '" + nombre_usuario + "' "
    "ORDER BY fecha_creacion DESC LIMIT 20"
)
conexion = obtener_conexion()
cur = conexion.cursor()
cur.execute(consulta)
```

**Código corregido (después):**
```python
consulta = (
    "SELECT id, contenido, fecha_creacion FROM publicaciones "
    "WHERE usuario = %s "
    "ORDER BY fecha_creacion DESC LIMIT 20"
)
conexion = obtener_conexion()
cur = conexion.cursor()
cur.execute(consulta, (nombre_usuario,))
```

**Por qué esto previene el ataque:**

- El driver `psycopg2` trata el valor de `nombre_usuario` como dato puro,
  nunca como parte de la instrucción SQL.
- Cualquier caracter especial (`'`, `"`, `;`, `--`, etc.) se escapa
  automáticamente antes de enviarse al servidor PostgreSQL.
- Un payload como `' OR '1'='1` se busca literalmente como nombre de usuario,
  no como lógica SQL.

**Validación adicional aplicada:**

Se agrega también una validación de longitud máxima para descartar entradas
obviamente maliciosas antes de llegar a la base de datos:

```python
if len(nombre_usuario) > 50:
    return jsonify({"error": "Nombre de usuario demasiado largo"}), 400
```

### Prueba de regresión

Con el código corregido, el siguiente payload ya NO retorna filas adicionales
ni genera error en la base de datos — simplemente busca el string literal:

```
GET /publicaciones/buscar?usuario=' OR '1'='1
→ {"usuario": "' OR '1'='1", "publicaciones": []}
```

El pipeline en verde confirma que Bandit ya no detecta B608 en el archivo
remediado.
