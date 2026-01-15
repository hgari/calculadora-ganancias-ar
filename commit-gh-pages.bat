@echo off
REM Script simple para commitear y pushear cambios en gh-pages (Windows)
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   Commit en rama gh-pages
echo ========================================
echo.

REM Verificar que estamos en gh-pages
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

if not "%CURRENT_BRANCH%"=="gh-pages" (
    echo [ERROR] Debes estar en la rama gh-pages para usar este script
    echo Rama actual: %CURRENT_BRANCH%
    echo.
    echo Usa deploy-gh-pages.bat para hacer un deploy completo desde main
    pause
    exit /b 1
)

echo Rama actual: gh-pages [OK]
echo.

REM Mostrar estado
echo Archivos modificados:
git status --short
echo.

REM Pedir mensaje de commit
set /p COMMIT_MSG="Mensaje del commit (Enter para usar mensaje por defecto): "

if "%COMMIT_MSG%"=="" (
    REM Usar mensaje por defecto con fecha/hora
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATE=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set TIME=%%a:%%b)
    set COMMIT_MSG=Actualizar frontend - %DATE% %TIME%
)

echo.
echo Mensaje: %COMMIT_MSG%
echo.

REM Preguntar si quiere continuar
set /p CONFIRM="Continuar con commit y push? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Cancelado por el usuario
    pause
    exit /b 0
)

echo.
echo [1/3] Agregando archivos...
git add .

echo.
echo [2/3] Commiteando...
git commit -m "%COMMIT_MSG%"

if errorlevel 1 (
    echo [WARNING] No hay cambios para commitear o hubo un error
    pause
    exit /b 1
)

echo.
echo [3/3] Subiendo a GitHub...
git push origin gh-pages

if errorlevel 1 (
    echo [ERROR] Hubo un problema al hacer push
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Cambios subidos exitosamente!
echo ========================================
echo.
echo Los cambios estaran visibles en unos minutos en:
echo https://hgari.github.io/calculadora-ganancias-ar/
echo.

pause
