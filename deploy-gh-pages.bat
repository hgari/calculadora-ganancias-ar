@echo off
REM Script para desplegar frontend a GitHub Pages (Windows)
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   Deploy a GitHub Pages
echo ========================================
echo.

REM Verificar que estamos en la rama main
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

if not "%CURRENT_BRANCH%"=="main" (
    echo [WARNING] No estas en la rama main. Cambiando a main...
    git checkout main
    if errorlevel 1 (
        echo [ERROR] No se pudo cambiar a la rama main
        pause
        exit /b 1
    )
)

REM Verificar que no hay cambios sin commitear
git diff-index --quiet HEAD -- 2>nul
if errorlevel 1 (
    echo [ERROR] Hay cambios sin commitear. Por favor, hace commit primero.
    echo.
    git status --short
    pause
    exit /b 1
)

echo [OK] Verificaciones completadas
echo.

REM Preguntar si quiere continuar
set /p CONFIRM="Desplegar frontend a GitHub Pages? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Cancelado por el usuario
    pause
    exit /b 0
)

echo.
echo [1/5] Cambiando a rama gh-pages...

REM Verificar si existe la rama gh-pages
git show-ref --verify --quiet refs/heads/gh-pages
if errorlevel 1 (
    echo [INFO] Creando rama gh-pages por primera vez...
    git checkout --orphan gh-pages
) else (
    echo [INFO] Rama gh-pages ya existe, cambiando...
    git checkout gh-pages
    if errorlevel 1 (
        echo [ERROR] No se pudo cambiar a gh-pages
        pause
        exit /b 1
    )
)

REM VERIFICACION CRITICA: Asegurarnos que estamos en gh-pages
for /f "tokens=*" %%i in ('git branch --show-current') do set VERIFY_BRANCH=%%i
if not "%VERIFY_BRANCH%"=="gh-pages" (
    echo [ERROR CRITICO] No estamos en gh-pages! Abortando por seguridad.
    echo Rama actual: %VERIFY_BRANCH%
    git checkout main
    pause
    exit /b 1
)

echo [OK] Confirmado: estamos en gh-pages
echo.

echo [2/5] Limpiando archivos antiguos...

REM Limpiar solo archivos específicos, no todo
if exist index.html del /f /q index.html
if exist app.js del /f /q app.js
if exist style.css del /f /q style.css
if exist config.js del /f /q config.js
if exist server.py del /f /q server.py
if exist .nojekyll del /f /q .nojekyll

echo.
echo [3/5] Copiando archivos del frontend desde main...

git checkout main -- frontend/

if not exist frontend (
    echo [ERROR] No se pudo copiar la carpeta frontend
    git checkout main
    pause
    exit /b 1
)

echo.
echo [4/5] Moviendo archivos a la raiz...

REM Mover archivos del frontend a la raíz
move /Y frontend\*.html . >nul 2>&1
move /Y frontend\*.js . >nul 2>&1
move /Y frontend\*.css . >nul 2>&1
move /Y frontend\*.py . >nul 2>&1
rmdir frontend

REM Crear .nojekyll
type nul > .nojekyll

echo.
echo [5/5] Commiteando y subiendo cambios...

git add .

REM Obtener fecha y hora para el commit
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATE=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set TIME=%%a:%%b)

git commit -m "Deploy frontend - %DATE% %TIME%"
if errorlevel 1 (
    echo [INFO] No hay cambios nuevos para commitear
) else (
    echo [OK] Commit exitoso
)

echo.
echo Subiendo a GitHub...
git push origin gh-pages

if errorlevel 1 (
    echo [ERROR] Hubo un problema al hacer push
    git checkout main
    pause
    exit /b 1
)

echo.
echo [OK] Volviendo a main...
git checkout main

echo.
echo ========================================
echo   Deploy completado exitosamente!
echo ========================================
echo.
echo Tu frontend estara disponible en unos minutos en:
echo https://hgari.github.io/calculadora-ganancias-ar/
echo.
echo Verifica el estado en:
echo https://github.com/hgari/calculadora-ganancias-ar/settings/pages
echo.

pause
