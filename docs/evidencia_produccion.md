# Evidencia de Producción

**Proyecto:** PacFeed — Red social de formato corto  
**Instancia de Producción:** [COMPLETAR — IP pública de la instancia nueva]  
**Fecha de deploy:** [COMPLETAR]

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
- **IP pública:** [COMPLETAR tras crear la instancia]
- **AMI utilizada:** [COMPLETAR — misma que QA para consistencia]
- **Tipo:** t3.micro
- **Región:** us-east-1

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
