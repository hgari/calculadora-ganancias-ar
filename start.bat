@echo off
setlocal

echo ============================================================
echo   Calculadora Impuesto a las Ganancias - Argentina
echo ============================================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo Iniciando servidores...
echo.

REM Iniciar backend en una nueva ventana
echo Iniciando Backend en http://localhost:8000
start "Backend - Ganancias" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Esperar 3 segundos para que el backend se inicie
timeout /t 3 /nobreak >nul

REM Iniciar frontend en una nueva ventana
echo Iniciando Frontend (puerto 8080 o siguiente disponible)
start "Frontend - Ganancias" cmd /k "cd frontend && python server.py"

echo.
echo ============================================================
echo Servidores iniciados en ventanas separadas:
echo   * Backend:  http://localhost:8000
echo   * Frontend: http://localhost:8080 (o siguiente puerto)
echo ============================================================
echo.
echo Abre http://localhost:8080 en tu navegador
echo Cierra las ventanas de cmd para detener los servidores
echo.
pause
