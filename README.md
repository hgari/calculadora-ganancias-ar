# Calculadora Impuesto a las Ganancias - Argentina

Calculadora web del Impuesto a las Ganancias (Cuarta Categoría) para Argentina, año 2026.

## Stack Técnico

- **Backend**: Python con FastAPI
- **Frontend**: HTML/CSS/JavaScript vanilla
- **Datos**: JSON (tablas de deducciones y escalas)

## Funcionalidades

- Cálculo automático de descuentos obligatorios (jubilación, obra social, PAMI, Ley 19.032)
- Deducciones personales (GNI, deducción especial, cargas de familia)
- Deducciones opcionales (alquiler, prepaga, seguros, etc.)
- Aplicación de escala progresiva del impuesto
- Desglose detallado paso a paso
- Interfaz responsive y fácil de usar

## Estructura del Proyecto

```
calculadora-ganancias-ar/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── calculator.py        # Lógica de cálculo
│   └── data/
│       ├── deducciones_2026.json
│       └── escalas_2026.json
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
└── README.md
```

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip

### Inicio Rápido (Recomendado)

Instalar dependencias y ejecutar ambos servidores:

**Windows:**
```bash
pip install -r requirements.txt
start.bat
```

**Linux/Mac:**
```bash
pip install -r requirements.txt
chmod +x start.sh
./start.sh
```

**Multiplataforma (Python):**
```bash
pip install -r requirements.txt
python start.py
```

Esto iniciará automáticamente el backend (puerto 8000) y el frontend (puerto 8080 o siguiente disponible).

### Ejecución Manual

#### Backend

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Iniciar el servidor:

**Opción 1 (recomendada con auto-reload):**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Opción 2 (usando el script):**
```bash
cd backend
python run.py
```

**Opción 3 (producción):**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servidor estará disponible en `http://localhost:8000`

#### Frontend

**Opción 1 (servidor Python con CORS):**
```bash
cd frontend
python server.py
```

**Opción 2 (servidor HTTP simple):**
```bash
cd frontend
python -m http.server 8080
```

**Opción 3 (usando Node.js con http-server):**
```bash
cd frontend
npx http-server -p 8080 --cors
```

**Opción 4 (abrir directamente el archivo):**
- Abrir `frontend/index.html` directamente en el navegador
- Nota: Puede tener problemas de CORS con esta opción

El frontend estará disponible en `http://localhost:8080`

## Uso

1. Ingresar el sueldo bruto mensual
2. Seleccionar estado civil
3. Indicar cantidad de hijos
4. Agregar deducciones opcionales si corresponde (alquiler, prepaga, etc.)
5. Hacer clic en "Calcular"
6. Revisar el desglose detallado del cálculo

## API Endpoints

### `POST /calcular`

Calcula el impuesto a las ganancias.

**Request:**
```json
{
  "sueldo_bruto": 1500000,
  "estado_civil": "casado",
  "cantidad_hijos": 2,
  "deducciones_opcionales": [
    {
      "concepto": "Alquiler",
      "monto": 300000
    }
  ]
}
```

**Response:**
```json
{
  "sueldo_bruto": 1500000,
  "descuentos_obligatorios": {...},
  "sueldo_neto": 1215000,
  "deducciones_personales": {...},
  "deducciones_opcionales": [...],
  "ganancia_neta_sujeta_mensual": 750000,
  "impuesto": {
    "impuesto_mensual": 45000,
    "impuesto_anual": 540000,
    "detalle_escalas": [...]
  },
  "sueldo_neto_final": 1170000,
  "porcentaje_efectivo": 3.0
}
```

### `GET /deducciones`

Obtiene las deducciones configuradas.

### `GET /escalas`

Obtiene las escalas progresivas configuradas.

## Configuración de Datos

Los archivos JSON en `backend/data/` contienen los valores actualizados:

- **deducciones_2026.json**: Montos de GNI, deducción especial, cargas de familia
- **escalas_2026.json**: Tramos y alícuotas de la escala progresiva

Para actualizar los valores, editar directamente estos archivos.

## Advertencia Legal

Esta calculadora es **orientativa** y los resultados deben ser confirmados con un contador matriculado. Los cálculos se basan en las normativas vigentes para el año 2026.

## Licencia

MIT

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abrir un issue o pull request.
