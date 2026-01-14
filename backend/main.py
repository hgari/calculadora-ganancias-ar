from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from calculator import CalculadoraGanancias

app = FastAPI(title="Calculadora Impuesto a las Ganancias - Argentina")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calculadora = CalculadoraGanancias()


class DeduccionOpcional(BaseModel):
    concepto: str
    monto: float
    tipo: str  # Clave para mapear con deducciones_opcionales en JSON


class CalculoRequest(BaseModel):
    sueldo_bruto: float
    estado_civil: str  # "soltero", "casado"
    cantidad_hijos: int
    deducciones_opcionales: Optional[List[DeduccionOpcional]] = []


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
