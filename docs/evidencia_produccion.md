# Evidencia de Producción

**Proyecto:** PacFeed — Red social de formato corto  
**Instancia de Producción:** 32.197.202.120 (i-0d8539d708128ef2c)  
**URL:** http://32.197.202.120:5000  
**Repositorio de Producción:** https://github.com/alanrivera066/Project_PacFeed_Prod  
**Fecha de deploy:** 25 de septiembre de 2026

---

## Confirmación del ciclo completo

| Paso | Estado | Evidencia |
|------|--------|-----------|
| Parche aplicado en QA | ✅ | Commit en rama main |
| Pipeline bloqueó el parche | ✅ | `reportes/pipeline_bloqueado.*` |
| Falla clasificada | ✅ | `docs/clasificacion_hallazgo.md` |
| Contención documentada | ✅ | `docs/respuesta_incidente.md` |
| Código remediado | ✅ | Commit de remediación en main |
| Pipeline en verde | ✅ | `reportes/pipeline_verde.*` |
| Deploy a Producción | ✅ | Capturas abajo |

---

## Instancia de Producción

- **Nombre:** pacfeed-prod
- **Instance ID:** i-0d8539d708128ef2c
- **IP pública:** 32.197.202.120
- **AMI utilizada:** ami-05dee78f58650ed2c (Amazon Linux 2023, misma que QA)
- **Tipo:** t3.micro
- **Región:** us-east-1 (us-east-1a)

## Verificación funcional realizada

Se comprobó por API sobre la instancia de Producción:

- `GET /salud` → `{"estado": "ok"}`
- Registro de usuario → OK
- Publicación → OK
- Búsqueda por usuario (`GET /publicaciones/buscar?usuario=...`) → devuelve resultados correctos
- Intento de inyección SQL (`usuario=' OR '1'='1`) → devuelve 0 resultados, confirmando que la falla remediada NO está presente en Producción

---

## Capturas de evidencia

### La aplicación corriendo en Producción

> Captura de pantalla de `http://<IP-PROD>:5000` mostrando la UI de PacFeed.

[INSERTAR CAPTURA]

### Health check respondiendo en Producción

```
curl http://<IP-PROD>:5000/salud
→ {"estado": "ok"}
```

[INSERTAR CAPTURA DEL TERMINAL O NAVEGADOR]

### Instancia en consola AWS

> Captura de la consola de AWS EC2 mostrando la instancia `pacfeed-prod` en
> estado **running**.

[INSERTAR CAPTURA]

---

## Notas

- La instancia de Producción solo recibió el código **ya remediado** (el que
  pasó el pipeline en verde). El parche con la falla nunca llegó aquí.
- La instancia se terminó inmediatamente después de tomar estas evidencias
  para conservar el crédito del Learner Lab.
