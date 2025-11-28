# Activa Supabase - Keep Alive Script

Script para mantener activas múltiples bases de datos de Supabase mediante consultas periódicas automáticas en Vercel.

## 🚀 Características

- ✅ Mantiene activas múltiples bases de datos de Supabase
- ✅ Ejecución automática cada 3 días mediante Vercel Cron Jobs
- ✅ Soporte para múltiples proyectos/cuentas de Supabase
- ✅ Despliegue simple en Vercel

## 📋 Configuración

### 1. Variables de Entorno

Configura la variable de entorno `SUPABASE_PROJECTS` en Vercel con el siguiente formato JSON:

```json
{
  "project1": {
    "url": "https://xxxxx.supabase.co",
    "key": "tu-anon-key-aqui",
    "table": "users"
  },
  "project2": {
    "url": "https://yyyyy.supabase.co",
    "key": "tu-anon-key-aqui",
    "table": "users"
  }
}
```

**Notas importantes:**
- Usa la **anon/public key**, NO la service_role key
- La tabla debe existir en cada proyecto
- Puedes agregar tantos proyectos como necesites

### 2. Configurar en Vercel

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Agrega `SUPABASE_PROJECTS` con tu JSON
4. Asegúrate de marcarlo para Production, Preview y Development

## 🛠️ Despliegue

### Opción 1: Vercel CLI

```bash
# Instalar Vercel CLI (si no lo tienes)
npm install -g vercel

# Iniciar sesión
vercel login

# Desplegar
vercel

# Desplegar a producción
vercel --prod
```

### Opción 2: GitHub Integration

1. Conecta tu repositorio a Vercel
2. Vercel detectará automáticamente el proyecto
3. Configura las variables de entorno en el dashboard
4. El despliegue se hará automáticamente

## ⏰ Configuración del Cron

El cron está configurado para ejecutarse cada 3 días a medianoche UTC (`0 0 */3 * *`).

Para cambiar la frecuencia, edita `vercel.json`:

- **Diario**: `"0 0 * * *"`
- **Cada 2 días**: `"0 0 */2 * *"`
- **Cada semana**: `"0 0 * * 0"`

## 🧪 Pruebas

Puedes probar la función manualmente visitando:
```
https://tu-proyecto.vercel.app/api/keep-alive
```

Deberías ver un JSON con los resultados de las consultas a cada proyecto.

## 📝 Estructura del Proyecto

```
activaSupabase/
├── api/
│   └── keep-alive.py    # Función serverless
├── vercel.json          # Configuración de cron jobs
├── requirements.txt     # Dependencias Python
├── .env.example         # Ejemplo de variables de entorno
└── README.md            # Este archivo
```

## 🔍 Verificación

1. Ve a Vercel Dashboard → Tu Proyecto → Settings → Cron Jobs
2. Verifica que el cron job esté configurado
3. Revisa los logs en Deployments para ver las ejecuciones

## ⚠️ Notas

- El cron job solo se activa en producción
- Las ejecuciones aparecen en los logs de Vercel
- Asegúrate de que las tablas especificadas existan en cada proyecto
- Usa siempre la anon/public key, nunca la service_role key

