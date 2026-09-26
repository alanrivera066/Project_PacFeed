# Secrets requeridos en GitHub Actions

Ve a tu repositorio en GitHub → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Valor |
|--------|-------|
| `QA_HOST` | IP pública de tu instancia EC2 `pacfeed-dev` (us-east-1a) |
| `QA_USER` | Usuario SSH de la instancia (normalmente `ec2-user` o `ubuntu`) |
| `QA_SSH_KEY` | Contenido completo de tu archivo `.pem` (incluye `-----BEGIN RSA PRIVATE KEY-----` y `-----END RSA PRIVATE KEY-----`) |

## Cómo obtener la IP de tu instancia QA

En la consola de AWS → EC2 → Instancias → selecciona `pacfeed-dev` → copia la **Public IPv4 address**.

## Cómo copiar el contenido del .pem

```powershell
Get-Content "C:\ruta\a\tu-key.pem" | clip
```

Luego pégalo en el campo del secret `QA_SSH_KEY`.
