import json
from pathlib import Path
from typing import List, Dict, Optional


class CalculadoraGanancias:
    def __init__(self):
        self.data_path = Path(__file__).parent / "data"
        self.deducciones = self._cargar_deducciones()
        self.escalas = self._cargar_escalas()

    def _cargar_deducciones(self) -> Dict:
        with open(self.data_path / "deducciones_2026.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _cargar_escalas(self) -> Dict:
        with open(self.data_path / "escalas_2026.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def obtener_deducciones(self) -> Dict:
        return self.deducciones

    def obtener_escalas(self) -> Dict:
        return self.escalas

    def calcular_descuentos_obligatorios(self, sueldo_bruto: float) -> Dict[str, float]:
        """
        Calcula los descuentos obligatorios (jubilación, obra social, ley 19.032)
        Total: 17% del bruto
        """
        porcentajes = self.deducciones["descuentos_obligatorios"]

        descuentos = {}
        total = 0

        descuentos["jubilacion"] = round(sueldo_bruto * porcentajes["jubilacion"], 2)
        descuentos["obra_social"] = round(sueldo_bruto * porcentajes["obra_social"], 2)
        descuentos["ley_19032"] = round(sueldo_bruto * porcentajes["ley_19032"], 2)

        descuentos["total"] = round(sueldo_bruto * porcentajes["total"], 2)
        return descuentos

    def calcular_deducciones_personales(self, estado_civil: str, cantidad_hijos: int, hijos_incapacitados: int = 0) -> Dict[str, float]:
        """
        Calcula las deducciones personales (GNI, deducción especial, cargas de familia)
        Valores actualizados para Enero-Junio 2026
        """
        deducciones_calc = {}

        # Ganancia No Imponible (GNI) - mensual
        deducciones_calc["gni_mensual"] = self.deducciones["gni_mensual"]
        deducciones_calc["gni_anual"] = self.deducciones["gni_anual"]

        # Deducción especial trabajadores - mensual
        deducciones_calc["deduccion_especial_mensual"] = self.deducciones["deduccion_especial_mensual"]
        deducciones_calc["deduccion_especial_anual"] = self.deducciones["deduccion_especial_anual"]

        # Cónyuge
        deducciones_calc["conyuge_mensual"] = 0
        deducciones_calc["conyuge_anual"] = 0
        if estado_civil == "casado":
            deducciones_calc["conyuge_mensual"] = self.deducciones["conyuge_mensual"]
            deducciones_calc["conyuge_anual"] = self.deducciones["conyuge_anual"]

        # Hijos
        hijos_normales = cantidad_hijos - hijos_incapacitados
        deducciones_calc["hijos_mensual"] = (
            hijos_normales * self.deducciones["hijo_mensual"] +
            hijos_incapacitados * self.deducciones["hijo_incapacitado_mensual"]
        )
        deducciones_calc["hijos_anual"] = (
            hijos_normales * self.deducciones["hijo_anual"] +
            hijos_incapacitados * self.deducciones["hijo_incapacitado_anual"]
        )

        # Total deducciones personales
        total_mensual = (
            deducciones_calc["gni_mensual"] +
            deducciones_calc["deduccion_especial_mensual"] +
            deducciones_calc["conyuge_mensual"] +
            deducciones_calc["hijos_mensual"]
        )
        total_anual = total_mensual * 12

        deducciones_calc["total_mensual"] = round(total_mensual, 2)
        deducciones_calc["total_anual"] = round(total_anual, 2)

        return deducciones_calc

    def aplicar_escala_progresiva(self, ganancia_neta_sujeta: float) -> Dict[str, float]:
        """
        Aplica la escala progresiva del impuesto
        """
        # Convertir a anual
        ganancia_anual = ganancia_neta_sujeta * 12

        impuesto_calculado = 0
        detalle_escalas = []

        for escala in self.escalas["escalas"]:
            desde = escala["desde"]
            hasta = escala["hasta"] if escala["hasta"] else float('inf')

            if ganancia_anual > desde:
                base_imponible = min(ganancia_anual, hasta) - desde
                impuesto_tramo = (base_imponible * escala["porcentaje"]) + escala["fijo"]

                detalle_escalas.append({
                    "desde": desde,
                    "hasta": hasta if hasta != float('inf') else "en adelante",
                    "porcentaje": escala["porcentaje"] * 100,
                    "fijo": escala["fijo"],
                    "base_imponible": round(base_imponible, 2),
                    "impuesto_tramo": round(impuesto_tramo, 2)
                })

                impuesto_calculado = impuesto_tramo

                if ganancia_anual <= hasta:
                    break

        return {
            "ganancia_anual": round(ganancia_anual, 2),
            "impuesto_anual": round(impuesto_calculado, 2),
            "impuesto_mensual": round(impuesto_calculado / 12, 2),
            "detalle_escalas": detalle_escalas
        }

    def calcular(self, sueldo_bruto: float, estado_civil: str, cantidad_hijos: int,
                 deducciones_opcionales: Optional[List] = None) -> Dict:
        """
        Realiza el cálculo completo del impuesto a las ganancias
        """
        if deducciones_opcionales is None:
            deducciones_opcionales = []

        # 1. Calcular descuentos obligatorios
        descuentos = self.calcular_descuentos_obligatorios(sueldo_bruto)

        # 2. Sueldo neto después de descuentos
        sueldo_neto = sueldo_bruto - descuentos["total"]

        # 3. Calcular deducciones personales
        deducciones_personales = self.calcular_deducciones_personales(estado_civil, cantidad_hijos)

        # 4. Deducciones opcionales (convertir a mensual)
        total_deducciones_opcionales = 0
        deducciones_opcionales_detalle = []

        for deduccion in deducciones_opcionales:
            monto = deduccion.get("monto", 0) if isinstance(deduccion, dict) else deduccion.monto
            concepto = deduccion.get("concepto", "") if isinstance(deduccion, dict) else deduccion.concepto
            tipo = deduccion.get("tipo", "") if isinstance(deduccion, dict) else deduccion.tipo

            # Obtener configuración de la deducción
            config = self.deducciones["deducciones_opcionales"].get(tipo, {})
            porcentaje_deducible = config.get("porcentaje_deducible", 1.0)

            # Aplicar porcentaje deducible
            monto_deducible = monto * porcentaje_deducible

            # Aplicar tope anual si existe (convertir a mensual para comparar)
            tope_anual = config.get("tope_anual")
            if tope_anual:
                # El monto viene mensual, anualizar para comparar con tope
                monto_deducible_anual = monto_deducible * 12
                if monto_deducible_anual > tope_anual:
                    # Limitar al tope y volver a mensual
                    monto_deducible = tope_anual / 12

            total_deducciones_opcionales += monto_deducible
            deducciones_opcionales_detalle.append({
                "concepto": concepto,
                "monto": round(monto_deducible, 2)
            })

        # 5. Ganancia neta sujeta a impuesto (mensual)
        ganancia_neta_sujeta = sueldo_neto - deducciones_personales["total_mensual"] - total_deducciones_opcionales

        # Si la ganancia neta es negativa o cero, no hay impuesto
        if ganancia_neta_sujeta <= 0:
            return {
                "sueldo_bruto": round(sueldo_bruto, 2),
                "descuentos_obligatorios": descuentos,
                "sueldo_neto": round(sueldo_neto, 2),
                "deducciones_personales": deducciones_personales,
                "deducciones_opcionales": deducciones_opcionales_detalle,
                "total_deducciones_opcionales": round(total_deducciones_opcionales, 2),
                "ganancia_neta_sujeta_mensual": 0,
                "impuesto": {
                    "impuesto_mensual": 0,
                    "impuesto_anual": 0,
                    "detalle_escalas": []
                },
                "sueldo_neto_final": round(sueldo_neto, 2),
                "mensaje": "No alcanza el mínimo no imponible"
            }

        # 6. Aplicar escala progresiva
        impuesto = self.aplicar_escala_progresiva(ganancia_neta_sujeta)

        # 7. Sueldo neto final
        sueldo_neto_final = sueldo_neto - impuesto["impuesto_mensual"]

        return {
            "sueldo_bruto": round(sueldo_bruto, 2),
            "descuentos_obligatorios": descuentos,
            "sueldo_neto": round(sueldo_neto, 2),
            "deducciones_personales": deducciones_personales,
            "deducciones_opcionales": deducciones_opcionales_detalle,
            "total_deducciones_opcionales": round(total_deducciones_opcionales, 2),
            "ganancia_neta_sujeta_mensual": round(ganancia_neta_sujeta, 2),
            "impuesto": impuesto,
            "sueldo_neto_final": round(sueldo_neto_final, 2),
            "porcentaje_efectivo": round((impuesto["impuesto_mensual"] / sueldo_bruto) * 100, 2)
        }
