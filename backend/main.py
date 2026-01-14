from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import tempfile
from calculator import CalculadoraGanancias
from f572_parser import F572Parser

app = FastAPI(title="Calculadora Impuesto a las Ganancias - Argentina")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calculadora = CalculadoraGanancias()
parser_f572 = F572Parser()


class DeduccionOpcional(BaseModel):
    concepto: str
    monto: float
    tipo: str  # Clave para mapear con deducciones_opcionales en JSON


class CalculoRequest(BaseModel):
    sueldo_bruto: float
    estado_civil: str  # "soltero", "casado"
    cantidad_hijos: int
    deducciones_opcionales: Optional[List[DeduccionOpcional]] = []


class DatosAcumulados(BaseModel):
    ingresos_acumulados: float
    deducciones_acumuladas: float
    impuesto_retenido_acumulado: Optional[float] = 0


class CalculoAnualRequest(BaseModel):
    mes_actual: CalculoRequest
    datos_acumulados: Optional[DatosAcumulados] = None
    mes_actual_numero: int  # 1-12, para calcular meses restantes


@app.get("/")
async def root():
    return {
        "mensaje": "API Calculadora de Ganancias Argentina",
        "version": "1.0",
        "endpoints": ["/calcular", "/deducciones", "/escalas"]
    }


@app.post("/calcular")
async def calcular_ganancias(request: CalculoRequest):
    resultado = calculadora.calcular(
        sueldo_bruto=request.sueldo_bruto,
        estado_civil=request.estado_civil,
        cantidad_hijos=request.cantidad_hijos,
        deducciones_opcionales=request.deducciones_opcionales
    )
    return resultado


@app.get("/deducciones")
async def obtener_deducciones():
    return calculadora.obtener_deducciones()


@app.get("/escalas")
async def obtener_escalas():
    return calculadora.obtener_escalas()


@app.post("/calcular-anual")
async def calcular_anual(request: CalculoAnualRequest):
    datos_acumulados_dict = request.datos_acumulados.dict() if request.datos_acumulados else None
    resultado = calculadora.calcular_anual_con_acumulados(
        mes_actual=request.mes_actual.dict(),
        datos_acumulados=datos_acumulados_dict,
        mes_actual_numero=request.mes_actual_numero
    )
    return resultado


@app.post("/upload-f572")
async def upload_f572(file: UploadFile = File(...)):
    """
    Sube y parsea un archivo PDF del formulario F.572.
    Extrae deducciones opcionales aplicadas en meses anteriores.
    Aplica topes automáticamente si las deducciones exceden los límites.

    Returns:
        {
            "meses_anteriores": [...],
            "deducciones_detalle": {...},
            "deducciones_con_topes": {...},
            "topes_aplicados": [...]
        }
    """
    # Validar que sea un PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    # Guardar archivo temporalmente
    temp_file = None
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Parsear el PDF
        resultado_parser = parser_f572.parse_pdf(temp_file_path)

        # Debug: Imprimir lo que se extrajo
        print(f"DEBUG - Meses anteriores extraídos: {resultado_parser['meses_anteriores']}")
        print(f"DEBUG - Deducciones detalle extraídas: {resultado_parser['deducciones_detalle']}")

        # Aplicar topes a las deducciones
        deducciones_con_topes = parser_f572.aplicar_topes(
            resultado_parser["deducciones_detalle"],
            calculadora
        )

        # Identificar qué deducciones fueron limitadas por topes
        topes_aplicados = []
        for tipo, monto_original in resultado_parser["deducciones_detalle"].items():
            monto_con_tope = deducciones_con_topes.get(tipo, 0)
            if monto_con_tope < monto_original:
                topes_aplicados.append({
                    "tipo": tipo,
                    "monto_original": monto_original,
                    "monto_con_tope": monto_con_tope,
                    "diferencia": monto_original - monto_con_tope
                })

        return {
            "success": True,
            "meses_anteriores": resultado_parser["meses_anteriores"],
            "deducciones_detalle": resultado_parser["deducciones_detalle"],
            "deducciones_con_topes": deducciones_con_topes,
            "topes_aplicados": topes_aplicados
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

    finally:
        # Eliminar archivo temporal
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
