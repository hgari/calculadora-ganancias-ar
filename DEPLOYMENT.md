# Guía de Despliegue - Calculadora de Ganancias

Esta guía te muestra cómo desplegar la aplicación de forma **100% gratuita** usando:
- **Backend**: Render.com (Free tier)
- **Frontend**: GitHub Pages (Gratis ilimitado)

---

## Paso 1: Desplegar el Backend en Render.com

### 1.1 Crear cuenta en Render
1. Ve a https://render.com
2. Regístrate con tu cuenta de GitHub (recomendado)

### 1.2 Conectar tu repositorio
1. En Render, click en **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub: `calculadora-ganancias-ar`
3. Render detectará automáticamente el archivo `render.yaml`

### 1.3 Configurar el servicio
Render debería detectar automáticamente la configuración, pero verifica:

- **Name**: `calculadora-ganancias-backend` (o el nombre que prefieras)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free`

### 1.4 Deploy
1. Click en **"Create Web Service"**
2. Espera 2-5 minutos mientras Render construye y despliega
3. Una vez completado, verás una URL como: `https://calculadora-ganancias-backend.onrender.com`

### 1.5 Verificar que funciona
Abre en tu navegador:
```
https://TU-URL.onrender.com/
```

Deberías ver:
```json
{
  "mensaje": "API Calculadora de Ganancias Argentina",
  "version": "1.0",
  "endpoints": ["/calcular", "/deducciones", "/escalas"]
}
```

---

## Paso 2: Configurar el Frontend para GitHub Pages

### 2.1 Actualizar la URL del backend
1. Abre el archivo `frontend/config.js`
2. Reemplaza `'https://calculadora-ganancias-backend.onrender.com'` con tu URL real de Render
3. Ejemplo:
```javascript
const API_CONFIG = {
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://TU-NOMBRE-backend.onrender.com'  // ← Cambiá esto
};
```

### 2.2 Crear rama gh-pages
En tu terminal, desde la raíz del proyecto:

```bash
# Crear una rama nueva para GitHub Pages
git checkout --orphan gh-pages

# Limpiar todo
git rm -rf .

# Copiar solo los archivos del frontend
git checkout main -- frontend/*

# Mover los archivos a la raíz
mv frontend/* .
rmdir frontend

# Agregar y commitear
git add .
git commit -m "Deploy frontend to GitHub Pages"

# Subir a GitHub
git push origin gh-pages

# Volver a la rama main
git checkout main
```

### 2.3 Activar GitHub Pages
1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Pages**
3. En **Source**, selecciona:
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
4. Click en **Save**
5. Espera 1-2 minutos

### 2.4 Acceder a tu sitio
Tu frontend estará disponible en:
```
https://TU-USUARIO.github.io/calculadora-ganancias-ar/
```

---

## Paso 3: Verificar que todo funciona

### 3.1 Probar el frontend
1. Abre tu URL de GitHub Pages
2. Ingresa datos en el formulario
3. Click en "Calcular"
4. Deberías ver los resultados correctamente

### 3.2 Debugging en caso de errores

**Si no se conecta al backend:**
1. Abre las DevTools del navegador (F12)
2. Ve a la pestaña **Console**
3. Busca errores de CORS o fetch

**Error común: Mixed Content**
- Si tu frontend está en HTTPS pero el backend en HTTP, no funcionará
- Render siempre usa HTTPS, así que esto no debería pasar

**Error: Backend se queda dormido**
- El free tier de Render suspende el servicio tras 15 min de inactividad
- La primera petición después de dormir tarda ~30 segundos
- Esto es normal y no se puede evitar en el plan gratuito

---

## Alternativa: Script automatizado (Opcional)

Creé un script que facilita el despliegue. Para usarlo:

```bash
# Hacer el script ejecutable (Linux/Mac)
chmod +x deploy-frontend.sh

# Ejecutar
./deploy-frontend.sh
```

---

## Resumen de URLs

Después de completar todo:

| Componente | URL |
|------------|-----|
| Backend API | `https://TU-NOMBRE.onrender.com` |
| Frontend | `https://TU-USUARIO.github.io/calculadora-ganancias-ar/` |
| Repositorio | `https://github.com/TU-USUARIO/calculadora-ganancias-ar` |

---

## Costos

- **Backend (Render)**: $0/mes (con limitaciones)
  - 750 horas/mes gratis
  - Se suspende tras 15 min de inactividad
  - ~30 seg para "despertar"

- **Frontend (GitHub Pages)**: $0/mes
  - Ilimitado
  - CDN global
  - Sin suspensiones

**Total: $0/mes** ✅

---

## Actualizaciones futuras

### Para actualizar el backend:
```bash
git add .
git commit -m "Actualización del backend"
git push origin main
```
Render detecta el push y redespliega automáticamente.

### Para actualizar el frontend:
```bash
# Hacer cambios en la carpeta frontend/
git add .
git commit -m "Actualización del frontend"
git push origin main

# Actualizar gh-pages
git checkout gh-pages
git checkout main -- frontend/*
mv frontend/* .
rmdir frontend
git add .
git commit -m "Deploy frontend update"
git push origin gh-pages
git checkout main
```

O usar el script: `./deploy-frontend.sh`

---

## Soporte

Si tenés problemas:
1. Revisa los logs en Render: Dashboard → Tu servicio → Logs
2. Revisa la consola del navegador (F12)
3. Verifica que las URLs estén correctamente configuradas en `frontend/config.js`

¡Listo! Tu aplicación debería estar corriendo en la nube de forma gratuita.
