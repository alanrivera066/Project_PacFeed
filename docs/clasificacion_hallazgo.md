# Clasificación del Hallazgo de Seguridad

**Proyecto:** PacFeed — Red social de formato corto  
**Archivo afectado:** `app/buscar_publicaciones.py`  
**Endpoint afectado:** `GET /publicaciones/buscar?usuario=...`  
**Detectado por:** Bandit (regla B608 — hardcoded SQL expressions)  
**Fecha de detección:** Pipeline de QA — corrida bloqueada

---

## Hallazgo

El endpoint `/publicaciones/buscar` recibe el parámetro `usuario` desde la query
string y lo concatena directamente dentro de un string SQL antes de ejecutarlo:

```python
# Código vulnerable (buscar_publicaciones.py, líneas 34-37)
consulta = (
    "SELECT id, contenido, fecha_creacion FROM publicaciones "
    "WHERE usuario = '" + nombre_usuario + "' "
    "ORDER BY fecha_creacion DESC LIMIT 20"
)
```

Un atacante puede enviar un valor malicioso como `usuario` y modificar la lógica
de la consulta a voluntad.

---

## Tipo de falla

| Campo | Detalle |
|-------|---------|
| **Categoría** | Inyección SQL (SQL Injection) |
| **CWE** | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — Improper Neutralization of Special Elements used in an SQL Command |
| **OWASP Top 10** | A03:2021 — Injection |
| **Regla Bandit** | B608 — possible SQL injection via string-based query construction |

---

## Severidad

**Nivel: ALTA**

| Criterio | Evaluación |
|----------|-----------|
| **Impacto** | Un atacante puede leer cualquier tabla de la base de datos, modificar o eliminar registros, y potencialmente escalar privilegios en el sistema. La tabla `users` contiene hashes de contraseñas que podrían ser crackeados. |
| **Facilidad de explotación** | Muy fácil. El parámetro vulnerable está expuesto en la URL sin ninguna validación ni autenticación requerida. Solo se necesita un navegador o `curl`. |
| **Autenticación requerida** | No — el endpoint no exige el header `X-User-Id`. |
| **Condiciones especiales** | Ninguna. El exploit funciona directamente. |

**Ejemplos de payloads funcionales:**

```
# Listar todos los usuarios sin importar el nombre
GET /publicaciones/buscar?usuario=' OR '1'='1

# Extraer hashes de contraseñas (UNION-based)
GET /publicaciones/buscar?usuario=' UNION SELECT id, password_hash, created_at FROM users--

# Eliminar datos
GET /publicaciones/buscar?usuario='; DROP TABLE publicaciones; --
```

---

## ¿Falso positivo?

**No es un falso positivo.**

Se confirmó manualmente que la concatenación del parámetro `nombre_usuario`
se ejecuta tal cual sobre la base de datos PostgreSQL. No existe ningún mecanismo
de escapado, lista blanca, ni validación de entrada. El parámetro llega directamente
de `request.args.get("usuario", "")` sin ningún tratamiento previo.

Bandit marcó correctamente la línea con severidad MEDIUM/HIGH bajo la regla B608.
El hallazgo es válido y explotable en el entorno real.
