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

        # 4. Deducciones opcionales (tomar monto mensual tal cual)
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

            # NO aplicar tope aquí - tomar el monto tal cual
            # El tope se verificará mes a mes acumulado cuando se use con datos acumulados

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

    def calcular_anual_con_acumulados(self, mes_actual: Dict, datos_acumulados: Optional[Dict], mes_actual_numero: int) -> Dict:
        """
        Calcula la proyección anual del impuesto considerando totales acumulados del año.

        Args:
            mes_actual: Dict con datos del mes actual (sueldo_bruto, estado_civil, cantidad_hijos, deducciones_opcionales)
            datos_acumulados: Dict con ingresos_acumulados y deducciones_acumuladas de meses anteriores
            mes_actual_numero: int (1-12) para calcular meses restantes

        Returns:
            Dict con proyección anual, diferencia, sugerencia de ajuste y resumen mensual
        """
        # 1. Calcular el mes actual con el método existente
        calculo_mes_actual = self.calcular(
            sueldo_bruto=mes_actual["sueldo_bruto"],
            estado_civil=mes_actual["estado_civil"],
            cantidad_hijos=mes_actual["cantidad_hijos"],
            deducciones_opcionales=mes_actual.get("deducciones_opcionales", [])
        )

        ganancia_neta_actual = calculo_mes_actual["ganancia_neta_sujeta_mensual"]

        # 2. Calcular ganancia neta acumulada de meses anteriores
        ganancia_neta_acumulada = 0
        impuesto_ya_retenido_estimado = 0
        meses_anteriores_count = mes_actual_numero - 1

        if datos_acumulados:
            ingresos_acumulados = datos_acumulados["ingresos_acumulados"]
            deducciones_acumuladas = datos_acumulados["deducciones_acumuladas"]
            impuesto_retenido_acumulado = datos_acumulados.get("impuesto_retenido_acumulado", 0)

            # Calcular descuentos obligatorios del total acumulado
            descuentos_obligatorios_acumulados = ingresos_acumulados * 0.17
            sueldo_neto_acumulado = ingresos_acumulados - descuentos_obligatorios_acumulados

            # Calcular deducciones personales para los meses anteriores
            deducciones_personales = self.calcular_deducciones_personales(
                estado_civil=mes_actual["estado_civil"],
                cantidad_hijos=mes_actual["cantidad_hijos"]
            )
            deducciones_personales_acumuladas = deducciones_personales["total_mensual"] * meses_anteriores_count

            # Ganancia neta acumulada de meses anteriores
            ganancia_neta_acumulada = sueldo_neto_acumulado - deducciones_personales_acumuladas - deducciones_acumuladas
            ganancia_neta_acumulada = max(0, ganancia_neta_acumulada)

            # Si el usuario proveyó el impuesto ya retenido, usarlo directamente
            # Si no, estimarlo (promedio mensual aplicando escala)
            if impuesto_retenido_acumulado > 0:
                impuesto_ya_retenido_estimado = impuesto_retenido_acumulado
            elif meses_anteriores_count > 0:
                ganancia_neta_promedio_mes = ganancia_neta_acumulada / meses_anteriores_count
                impuesto_promedio = self.aplicar_escala_progresiva(ganancia_neta_promedio_mes)["impuesto_anual"] / 12
                impuesto_ya_retenido_estimado = impuesto_promedio * meses_anteriores_count

        # 3. Proyección de meses restantes
        meses_restantes = 12 - mes_actual_numero
        ganancia_neta_proyectada = ganancia_neta_actual * meses_restantes

        # 4. Calcular impuesto anual real sobre la ganancia total
        ganancia_neta_anual_total = ganancia_neta_acumulada + ganancia_neta_actual + ganancia_neta_proyectada

        # Aplicar escala progresiva sobre el total anual
        impuesto_anual_real = 0
        detalle_escalas = []

        for escala in self.escalas["escalas"]:
            desde = escala["desde"]
            hasta = escala["hasta"] if escala["hasta"] else float('inf')

            if ganancia_neta_anual_total > desde:
                base_imponible = min(ganancia_neta_anual_total, hasta) - desde
                impuesto_tramo = (base_imponible * escala["porcentaje"]) + escala["fijo"]

                detalle_escalas.append({
                    "desde": desde,
                    "hasta": hasta if hasta != float('inf') else "en adelante",
                    "porcentaje": escala["porcentaje"] * 100,
                    "fijo": escala["fijo"],
                    "base_imponible": round(base_imponible, 2),
                    "impuesto_tramo": round(impuesto_tramo, 2)
                })

                impuesto_anual_real = impuesto_tramo

                if ganancia_neta_anual_total <= hasta:
                    break

        # 5. Añadir impuesto del mes actual al ya retenido estimado
        impuesto_ya_retenido_estimado += calculo_mes_actual["impuesto"]["impuesto_mensual"]

        # 6. Calcular diferencia
        diferencia = impuesto_ya_retenido_estimado - impuesto_anual_real
        diferencia_porcentual = (diferencia / impuesto_anual_real * 100) if impuesto_anual_real > 0 else 0

        # 7. Sugerencia de ajuste para meses restantes
        impuesto_pendiente = impuesto_anual_real - impuesto_ya_retenido_estimado
        retencion_mensual_sugerida = impuesto_pendiente / meses_restantes if meses_restantes > 0 else 0

        # 8. Crear resumen mensual simplificado
        resumen_mensual = []

        if meses_anteriores_count > 0 and ganancia_neta_acumulada > 0:
            resumen_mensual.append({
                "mes": f"Meses anteriores ({meses_anteriores_count})",
                "ganancia_neta_sujeta": round(ganancia_neta_acumulada, 2),
                "impuesto_estimado": round(impuesto_ya_retenido_estimado - calculo_mes_actual["impuesto"]["impuesto_mensual"], 2),
                "tipo": "historico"
            })

        resumen_mensual.append({
            "mes": "Mes actual",
            "ganancia_neta_sujeta": round(ganancia_neta_actual, 2),
            "impuesto_estimado": round(calculo_mes_actual["impuesto"]["impuesto_mensual"], 2),
            "tipo": "actual"
        })

        if meses_restantes > 0:
            resumen_mensual.append({
                "mes": f"Proyección ({meses_restantes} meses)",
                "ganancia_neta_sujeta": round(ganancia_neta_proyectada, 2),
                "impuesto_estimado": round(calculo_mes_actual["impuesto"]["impuesto_mensual"] * meses_restantes, 2),
                "tipo": "proyectado"
            })

        return {
            "impuesto_anual_real": round(impuesto_anual_real, 2),
            "impuesto_ya_retenido_estimado": round(impuesto_ya_retenido_estimado, 2),
            "diferencia": round(diferencia, 2),
            "diferencia_porcentual": round(diferencia_porcentual, 2),
            "diferencia_tipo": "a_favor" if diferencia > 0 else "en_contra" if diferencia < 0 else "equilibrado",
            "retencion_mensual_sugerida": round(retencion_mensual_sugerida, 2),
            "retencion_mensual_actual": round(calculo_mes_actual["impuesto"]["impuesto_mensual"], 2),
            "meses_restantes": meses_restantes,
            "ganancia_neta_anual_total": round(ganancia_neta_anual_total, 2),
            "resumen_mensual": resumen_mensual,
            "detalle_escalas": detalle_escalas,
            "calculo_mes_actual": calculo_mes_actual
        }

    def calcular_anual_con_historia(self, mes_actual: Dict, meses_anteriores: List[Dict], mes_actual_numero: int) -> Dict:
        """
        Calcula la proyección anual del impuesto considerando meses anteriores del año.

        Args:
            mes_actual: Dict con datos del mes actual (sueldo_bruto, estado_civil, cantidad_hijos, deducciones_opcionales)
            meses_anteriores: List[Dict] con datos de meses anteriores (mes, sueldo_bruto, deducciones_opcionales_total)
            mes_actual_numero: int (1-12) para calcular meses restantes

        Returns:
            Dict con proyección anual, diferencia, sugerencia de ajuste y resumen mensual
        """
        # 1. Calcular el mes actual con el método existente
        calculo_mes_actual = self.calcular(
            sueldo_bruto=mes_actual["sueldo_bruto"],
            estado_civil=mes_actual["estado_civil"],
            cantidad_hijos=mes_actual["cantidad_hijos"],
            deducciones_opcionales=mes_actual.get("deducciones_opcionales", [])
        )

        ganancia_neta_actual = calculo_mes_actual["ganancia_neta_sujeta_mensual"]

        # 2. Calcular ganancias netas de meses anteriores
        resumen_mensual = []
        ganancia_neta_acumulada = 0
        impuesto_ya_retenido_estimado = 0

        for mes_data in meses_anteriores:
            # Calcular descuentos obligatorios
            sueldo_bruto_mes = mes_data["sueldo_bruto"]
            descuentos_obligatorios = sueldo_bruto_mes * 0.17
            sueldo_neto_mes = sueldo_bruto_mes - descuentos_obligatorios

            # Calcular deducciones personales (usando valores actuales como aproximación en Fase 1)
            deducciones_personales = self.calcular_deducciones_personales(
                estado_civil=mes_actual["estado_civil"],
                cantidad_hijos=mes_actual["cantidad_hijos"]
            )

            # Restar deducciones opcionales ya aplicadas
            deducciones_opcionales_mes = mes_data["deducciones_opcionales_total"]

            # Ganancia neta sujeta del mes
            ganancia_neta_mes = sueldo_neto_mes - deducciones_personales["total_mensual"] - deducciones_opcionales_mes
            ganancia_neta_mes = max(0, ganancia_neta_mes)  # No puede ser negativa

            ganancia_neta_acumulada += ganancia_neta_mes

            # Estimar impuesto del mes (calcular como si fuera anual y dividir)
            ganancia_anual_estimada_mes = ganancia_neta_mes * 12
            impuesto_anual_estimado = self.aplicar_escala_progresiva(ganancia_neta_mes)["impuesto_anual"]
            impuesto_mensual_estimado = impuesto_anual_estimado / 12

            impuesto_ya_retenido_estimado += impuesto_mensual_estimado

            resumen_mensual.append({
                "mes": mes_data["mes"],
                "ganancia_neta_sujeta": round(ganancia_neta_mes, 2),
                "impuesto_estimado": round(impuesto_mensual_estimado, 2),
                "tipo": "historico"
            })

        # 3. Agregar mes actual al resumen
        resumen_mensual.append({
            "mes": "actual",
            "ganancia_neta_sujeta": round(ganancia_neta_actual, 2),
            "impuesto_estimado": round(calculo_mes_actual["impuesto"]["impuesto_mensual"], 2),
            "tipo": "actual"
        })

        ganancia_neta_acumulada += ganancia_neta_actual
        impuesto_ya_retenido_estimado += calculo_mes_actual["impuesto"]["impuesto_mensual"]

        # 4. Proyección de meses restantes
        meses_restantes = 12 - mes_actual_numero
        ganancia_neta_proyectada = ganancia_neta_actual * meses_restantes

        if meses_restantes > 0:
            resumen_mensual.append({
                "mes": f"proyeccion_{meses_restantes}_meses",
                "ganancia_neta_sujeta": round(ganancia_neta_proyectada, 2),
                "impuesto_estimado": round(calculo_mes_actual["impuesto"]["impuesto_mensual"] * meses_restantes, 2),
                "tipo": "proyectado"
            })

        # 5. Calcular impuesto anual real sobre la ganancia total
        ganancia_neta_anual_total = ganancia_neta_acumulada + ganancia_neta_proyectada

        # Aplicar escala progresiva sobre el total anual
        impuesto_anual_real = 0
        detalle_escalas = []

        for escala in self.escalas["escalas"]:
            desde = escala["desde"]
            hasta = escala["hasta"] if escala["hasta"] else float('inf')

            if ganancia_neta_anual_total > desde:
                base_imponible = min(ganancia_neta_anual_total, hasta) - desde
                impuesto_tramo = (base_imponible * escala["porcentaje"]) + escala["fijo"]

                detalle_escalas.append({
                    "desde": desde,
                    "hasta": hasta if hasta != float('inf') else "en adelante",
                    "porcentaje": escala["porcentaje"] * 100,
                    "fijo": escala["fijo"],
                    "base_imponible": round(base_imponible, 2),
                    "impuesto_tramo": round(impuesto_tramo, 2)
                })

                impuesto_anual_real = impuesto_tramo

                if ganancia_neta_anual_total <= hasta:
                    break

        # 6. Calcular diferencia
        diferencia = impuesto_ya_retenido_estimado - impuesto_anual_real
        diferencia_porcentual = (diferencia / impuesto_anual_real * 100) if impuesto_anual_real > 0 else 0

        # 7. Sugerencia de ajuste para meses restantes
        impuesto_pendiente = impuesto_anual_real - impuesto_ya_retenido_estimado
        retencion_mensual_sugerida = impuesto_pendiente / meses_restantes if meses_restantes > 0 else 0

        return {
            "impuesto_anual_real": round(impuesto_anual_real, 2),
            "impuesto_ya_retenido_estimado": round(impuesto_ya_retenido_estimado, 2),
            "diferencia": round(diferencia, 2),
            "diferencia_porcentual": round(diferencia_porcentual, 2),
            "diferencia_tipo": "a_favor" if diferencia > 0 else "en_contra" if diferencia < 0 else "equilibrado",
            "retencion_mensual_sugerida": round(retencion_mensual_sugerida, 2),
            "retencion_mensual_actual": round(calculo_mes_actual["impuesto"]["impuesto_mensual"], 2),
            "meses_restantes": meses_restantes,
            "ganancia_neta_anual_total": round(ganancia_neta_anual_total, 2),
            "resumen_mensual": resumen_mensual,
            "detalle_escalas": detalle_escalas,
            "calculo_mes_actual": calculo_mes_actual
        }
