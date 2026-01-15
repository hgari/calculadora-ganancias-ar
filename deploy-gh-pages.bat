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
git diff-index --quiet HEAD --
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
echo [1/5] Preparando rama gh-pages...

REM Verificar si existe la rama gh-pages
git show-ref --verify --quiet refs/heads/gh-pages
if errorlevel 1 (
    echo [INFO] Creando rama gh-pages por primera vez...
    git checkout --orphan gh-pages
    git rm -rf .
    git checkout main -- frontend/*
) else (
    echo [INFO] Rama gh-pages ya existe, actualizando...
    git checkout gh-pages
    if errorlevel 1 (
        echo [ERROR] No se pudo cambiar a gh-pages
        pause
        exit /b 1
    )
    git rm -rf .
    git checkout main -- frontend/*
)

echo.
echo [2/5] Moviendo archivos del frontend a la raiz...

REM Mover archivos del frontend a la raíz
if exist frontend (
    for %%F in (frontend\*) do move "%%F" .
    for /d %%D in (frontend\*) do move "%%D" .
    rmdir frontend
)

echo.
echo [3/5] Creando archivo .nojekyll...
type nul > .nojekyll

echo.
echo [4/5] Commiteando cambios...
git add .

REM Obtener fecha y hora para el commit
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATE=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set TIME=%%a:%%b)

git commit -m "Deploy frontend - %DATE% %TIME%"
if errorlevel 1 (
    echo [WARNING] No hay cambios para commitear o hubo un error
)

echo.
echo [5/5] Subiendo a GitHub...
git push origin gh-pages --force

if errorlevel 1 (
    echo [ERROR] Hubo un problema al hacer push
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
