#!/bin/bash

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "============================================================"
echo "  Calculadora Impuesto a las Ganancias - Argentina"
echo "============================================================"
echo -e "${NC}"

# Función para limpiar procesos al salir
cleanup() {
    echo -e "\n${YELLOW}Deteniendo servidores...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✓ Servidores detenidos${NC}"
    exit 0
}

# Registrar trap para Ctrl+C
trap cleanup SIGINT SIGTERM

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}✗ Error: Python no está instalado${NC}"
    exit 1
fi

# Usar python3 o python según disponibilidad
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

echo -e "${CYAN}Iniciando servidores...${NC}\n"

# Verificar dependencias
$PYTHON -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error: Dependencias no instaladas${NC}"
    echo -e "${YELLOW}Ejecuta: pip install -r requirements.txt${NC}"
    exit 1
fi

# Iniciar backend
cd backend
$PYTHON -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✓ Backend iniciado en http://localhost:8000${NC}"

# Esperar un poco para que el backend se inicie
sleep 2

# Iniciar frontend
cd frontend
$PYTHON server.py &
FRONTEND_PID=$!
cd ..

sleep 1
echo -e "${GREEN}✓ Frontend iniciado (verifica el puerto en la salida del servidor)${NC}"

echo -e "\n${BOLD}${BLUE}Servidores ejecutándose:${NC}"
echo -e "  ${GREEN}•${NC} Backend:  http://localhost:8000"
echo -e "  ${GREEN}•${NC} Frontend: http://localhost:8080 (o siguiente puerto disponible)"
echo -e "\n${YELLOW}Presiona Ctrl+C para detener ambos servidores${NC}\n"

# Mantener el script ejecutándose
wait
