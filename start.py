#!/usr/bin/env python
"""
Script para iniciar backend y frontend simultáneamente
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

processes = []

def signal_handler(sig, frame):
    """Maneja la señal de interrupción (Ctrl+C)"""
    print(f"\n{Colors.WARNING}Deteniendo servidores...{Colors.ENDC}")
    for process in processes:
        process.terminate()
    print(f"{Colors.OKGREEN}✓ Servidores detenidos{Colors.ENDC}")
    sys.exit(0)

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        return False

def main():
    # Registrar el manejador de señales
    signal.signal(signal.SIGINT, signal_handler)

    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 60)
    print("  Calculadora Impuesto a las Ganancias - Argentina")
    print("=" * 60)
    print(f"{Colors.ENDC}")

    # Verificar dependencias
    if not check_dependencies():
        print(f"{Colors.FAIL}✗ Error: Dependencias no instaladas{Colors.ENDC}")
        print(f"{Colors.WARNING}Ejecuta: pip install -r requirements.txt{Colors.ENDC}")
        sys.exit(1)

    # Directorio raíz del proyecto
    root_dir = Path(__file__).parent
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"

    print(f"{Colors.OKCYAN}Iniciando servidores...{Colors.ENDC}\n")

    # Iniciar backend
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(backend_process)
        print(f"{Colors.OKGREEN}✓ Backend iniciado en http://localhost:8000{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error al iniciar backend: {e}{Colors.ENDC}")
        sys.exit(1)

    # Esperar un poco para que el backend se inicie
    time.sleep(2)

    # Iniciar frontend
    try:
        frontend_process = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(frontend_process)

        # Leer la primera línea para obtener el puerto
        time.sleep(1)
        print(f"{Colors.OKGREEN}✓ Frontend iniciado (verifica el puerto en la salida del servidor){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error al iniciar frontend: {e}{Colors.ENDC}")
        backend_process.terminate()
        sys.exit(1)

    print(f"\n{Colors.BOLD}{Colors.OKBLUE}Servidores ejecutándose:{Colors.ENDC}")
    print(f"  • Backend:  http://localhost:8000")
    print(f"  • Frontend: http://localhost:8080 (o siguiente puerto disponible)")
    print(f"\n{Colors.WARNING}Presiona Ctrl+C para detener ambos servidores{Colors.ENDC}\n")

    # Mantener el script ejecutándose y mostrar logs
    try:
        while True:
            time.sleep(1)
            # Verificar si algún proceso terminó
            for process in processes:
                if process.poll() is not None:
                    print(f"{Colors.FAIL}✗ Un servidor se detuvo inesperadamente{Colors.ENDC}")
                    signal_handler(None, None)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
