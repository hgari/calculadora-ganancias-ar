# Calculadora Impuesto a las Ganancias - Argentina

Calculadora web del Impuesto a las Ganancias (Cuarta Categoría) para Argentina, año 2026.

**Valores actualizados**: Argentina 2026 (Enero-Junio) - Valores oficiales AFIP/ARCA actualizados con IPC 11.73%

## Stack Técnico

- **Backend**: Python con FastAPI
- **Frontend**: HTML/CSS/JavaScript vanilla
- **Datos**: JSON (tablas de deducciones y escalas)
- **PDF Parsing**: pdfplumber para lectura de formularios F.572

## Funcionalidades

- Cálculo automático de descuentos obligatorios (jubilación, obra social, PAMI, Ley 19.032)
- Deducciones personales (GNI, deducción especial, cónyuge, hijos, otras personas a cargo)
- **12 deducciones opcionales** (alquiler, prepaga, seguros, educación, servicio doméstico, etc.)
- Aplicación de escala progresiva del impuesto
- Desglose detallado paso a paso del cálculo
- **Carga de formularios F.572 Web** (PDF) para importar datos de meses anteriores
- **Cálculo mensual sin aplicación de topes** - Los topes anuales se verificarán acumulativamente
- **Acceso remoto configurable** - Permite usar la calculadora desde cualquier dispositivo en la red
- Interfaz responsive y fácil de usar

## Estructura del Proyecto

```
calculadora-ganancias-ar/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── calculator.py        # Lógica de cálculo
│   ├── f572_parser.py       # Parser de formularios F.572 (PDF)
│   └── data/
│       ├── deducciones_2026.json
│       └── escalas_2026.json
├── frontend/
│   ├── index.html
│   ├── config.js            # Configuración de API URL
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

## Configuración para Acceso Remoto

Si querés acceder a la calculadora desde otro dispositivo en tu red:

1. **Backend**: Ya está configurado para aceptar conexiones remotas (`--host 0.0.0.0`)

2. **Frontend**: Editá el archivo `frontend/config.js`:

   ```javascript
   // Opción 1: Descomentá y configurá manualmente
   API_CONFIG.API_URL = 'http://192.168.1.100:8000';  // Cambiá por tu IP

   // Opción 2: Usar detección automática (por defecto)
   // Si el frontend está en http://TU_IP:8080, automáticamente usará http://TU_IP:8000
   ```

3. **Encontrar tu IP**:
   - Windows: `ipconfig` (buscar "IPv4 Address")
   - Linux/Mac: `ifconfig` o `ip addr`

4. **Acceder desde otro dispositivo**: Abrí `http://TU_IP:8080` en el navegador

## Uso

### Cálculo Mensual Simple

1. Ingresar el sueldo bruto mensual
2. Seleccionar estado civil
3. Indicar cantidad de hijos
4. Indicar cantidad de otras personas a cargo (padres, hermanos, etc. sin ingresos)
5. Agregar deducciones opcionales si corresponde:
   - Alquiler de vivienda (inquilino o RELI)
   - Medicina prepaga / Obra social
   - Gastos médicos
   - Seguros de vida y retiro
   - Gastos educativos
   - Servicio doméstico
   - Intereses hipotecarios
   - Donaciones
   - Gastos de sepelio
   - Impuesto a débitos/créditos bancarios
   - Indumentaria laboral
6. Hacer clic en "Calcular Impuesto"
7. Revisar el desglose detallado del cálculo

**Nota importante**: El cálculo mensual toma los montos tal cual los ingresás, sin aplicar los topes anuales. Los topes se verificarán mes a mes cuando uses la funcionalidad de cálculo anual con meses anteriores.

### Cálculo Anual (Funcionalidad Futura)

En desarrollo: Podrás cargar tus formularios F.572 Web (PDF) de meses anteriores para:
- Calcular el impuesto anual proyectado
- Detectar si te retuvieron de más o de menos
- Recibir sugerencias de ajuste mensual para los meses restantes

## API Endpoints

### `POST /calcular`

Calcula el impuesto a las ganancias.

**Request:**
```json
{
  "sueldo_bruto": 1500000,
  "estado_civil": "casado",
  "cantidad_hijos": 2,
  "otras_cargas": 1,
  "deducciones_opcionales": [
    {
      "concepto": "Alquiler",
      "tipo": "alquiler_inquilino",
      "monto": 300000
    },
    {
      "concepto": "Medicina Prepaga",
      "tipo": "medicina_prepaga",
      "monto": 150000
    }
  ]
}
```

**Parámetros:**
- `sueldo_bruto` (float): Sueldo bruto mensual
- `estado_civil` (string): "soltero" o "casado"
- `cantidad_hijos` (int): Cantidad de hijos a cargo
- `otras_cargas` (int, opcional): Otras personas a cargo sin ingresos (default: 0)
- `deducciones_opcionales` (array, opcional): Lista de deducciones opcionales
  - `concepto` (string): Descripción de la deducción
  - `tipo` (string): Tipo de deducción (ver tipos disponibles abajo)
  - `monto` (float): Monto mensual de la deducción

**Tipos de deducciones opcionales disponibles:**
- `alquiler_inquilino`: Alquiler de vivienda (40% deducible)
- `alquiler_reli`: Alquiler con RELI (10% deducible)
- `medicina_prepaga`: Medicina prepaga / Obra social (100% deducible)
- `gastos_medicos`: Gastos médicos con factura (40% deducible)
- `seguro_vida`: Seguros de vida (100% deducible)
- `seguro_retiro`: Seguros de retiro privados (100% deducible)
- `gastos_educativos`: Gastos educativos de hijos < 24 años (40% deducible)
- `servicio_domestico`: Servicio doméstico (100% deducible)
- `intereses_hipotecarios`: Intereses hipotecarios (100% deducible)
- `donaciones`: Donaciones bancarizadas (100% deducible)
- `gastos_sepelio`: Gastos de sepelio (100% deducible)
- `impuesto_debitos_creditos`: Impuesto a débitos/créditos (33% deducible)
- `indumentaria_laboral`: Indumentaria laboral (100% deducible)

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

Los archivos JSON en `backend/data/` contienen los valores actualizados para 2026 (Enero-Junio):

- **deducciones_2026.json**: Montos de GNI, deducción especial, cargas de familia, y deducciones opcionales
  - GNI mensual: $364.646
  - Deducción especial mensual: $2.017.462
  - Cónyuge mensual: $343.397
  - Hijo mensual: $173.179
  - Otras personas a cargo mensual: $173.179
  - Topes de deducciones opcionales (alquiler, prepaga, educación, etc.)

- **escalas_2026.json**: Tramos y alícuotas de la escala progresiva
  - Actualizado con los valores vigentes para enero-junio 2026

### Cómo actualizar los valores

Para actualizar los valores cuando ARCA/AFIP publique nuevas actualizaciones:

1. **Editar `backend/data/deducciones_2026.json`**:
   ```json
   {
     "año": 2026,
     "periodo": "Julio-Diciembre 2026",  // Actualizar período
     "descripcion": "Deducciones oficiales AFIP/ARCA actualizadas con IPC XX.XX%",
     "gni_mensual": NUEVO_VALOR,  // Actualizar valores
     "deduccion_especial_mensual": NUEVO_VALOR,
     // ... etc
   }
   ```

2. **Editar `backend/data/escalas_2026.json`**:
   ```json
   {
     "año": 2026,
     "periodo": "Julio-Diciembre 2026",  // Actualizar período
     "escalas": [
       {
         "desde": 0,
         "hasta": NUEVO_VALOR,  // Actualizar límites
         "alicuota": 0.05
       },
       // ... etc
     ]
   }
   ```

3. **Reiniciar el backend** para que tome los nuevos valores

**Nota**: Por ahora la actualización es manual. En el futuro se podría implementar un script automático que consuma los valores de ARCA/AFIP.

## Resolución de Problemas

### No puedo acceder desde otro dispositivo

1. Verificá que el backend esté corriendo con `--host 0.0.0.0` (por defecto lo hace)
2. Editá `frontend/config.js` y configurá tu IP manualmente:
   ```javascript
   API_CONFIG.API_URL = 'http://TU_IP:8000';
   ```
3. Verificá que el firewall permita conexiones al puerto 8000 y 8080
4. Asegurate de estar en la misma red WiFi/LAN

### El cálculo no coincide con mi recibo de sueldo

Recordá que:
- El cálculo mensual toma los montos tal cual, sin aplicar topes anuales
- Los topes se verificarán acumulativamente cuando uses la funcionalidad de meses anteriores
- Los valores se actualizan semestralmente (enero y julio)
- Hay un límite de retención mensual del 35% del bruto
- Consultá siempre con un contador matriculado

### Error de CORS al acceder desde el navegador

Si abrís `index.html` directamente, podés tener problemas de CORS. Usá uno de los métodos del servidor frontend:
```bash
cd frontend
python server.py  # Opción recomendada
```

## Advertencia Legal

Esta calculadora es **orientativa** y los resultados deben ser confirmados con un contador matriculado. Los cálculos se basan en las normativas vigentes para el año 2026.

**Importante**:
- Los valores se actualizan semestralmente (enero y julio)
- El cálculo mensual NO aplica topes anuales automáticamente
- Existe un límite de retención mensual del 35% del sueldo bruto
- Las deducciones opcionales requieren documentación respaldatoria (facturas, contratos, etc.)

## Despliegue en la Nube (Gratis)

Querés alojar la aplicación en internet de forma gratuita? Seguí la guía completa en [DEPLOYMENT.md](DEPLOYMENT.md)

**Stack de despliegue recomendado:**
- Backend: Render.com (Free tier)
- Frontend: GitHub Pages (Gratis ilimitado)
- **Costo total: $0/mes**

El despliegue toma ~10 minutos y no requiere tarjeta de crédito.

## Licencia

MIT

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abrir un issue o pull request.
