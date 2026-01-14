import pdfplumber
import re
from typing import Dict, List, Optional


class F572Parser:
    """
    Parser para el formulario F.572 de AFIP/ARCA.
    Extrae deducciones opcionales y sueldos mensuales.
    """

    MESES = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    # Mapeo de conceptos del F.572 a tipos de deducciones
    MAPEO_DEDUCCIONES = {
        "cuotas médico asistenciales": "prepaga",
        "primas de seguro": "seguro_vida",
        "gastos de adquisición de indumentaria": "indumentaria",
        "gastos de educación": "educacion",
        "alquileres": "alquiler",
        "servicio doméstico": "servicio_domestico",
        "intereses hipotecarios": "credito_hipotecario"
    }

    def __init__(self):
        pass

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        Parsea un PDF del F.572 y extrae los datos relevantes.

        Returns:
            {
                "meses_anteriores": [
                    {
                        "mes": "enero",
                        "sueldo_bruto": 0,  # Si está en el PDF
                        "deducciones_opcionales_total": 12345.67
                    },
                    ...
                ],
                "deducciones_detalle": {
                    "prepaga": 123.45,
                    "seguro_vida": 67.89,
                    ...
                }
            }
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

                # Debug: mostrar primeras líneas del PDF
                print("=" * 80)
                print("DEBUG - Primeras 50 líneas del PDF extraído:")
                print("=" * 80)
                lines = text.split('\n')
                for i, line in enumerate(lines[:50]):
                    print(f"{i+1:3d}: {line}")
                print("=" * 80)

                # Extraer deducciones por mes
                deducciones_por_mes = self._extraer_deducciones_por_mes(text)

                # Extraer detalle de deducciones por tipo
                deducciones_detalle = self._extraer_deducciones_detalle(text)

                return {
                    "meses_anteriores": deducciones_por_mes,
                    "deducciones_detalle": deducciones_detalle
                }
        except Exception as e:
            raise Exception(f"Error al parsear PDF: {str(e)}")

    def _extraer_deducciones_por_mes(self, text: str) -> List[Dict]:
        """
        Extrae el total de deducciones opcionales por mes.
        Busca secciones con montos mensuales y los suma.
        """
        # Inicializar totales por mes
        totales_por_mes = {mes: 0.0 for mes in self.MESES}

        # El F.572 tiene subtotales por cada tipo de deducción
        # Buscar patrones como "Subtotal" seguido de montos mensuales
        lines = text.split('\n')

        # Buscar la línea de encabezado con meses
        idx_header_meses = -1
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Buscar línea que tenga "enero", "febrero", etc.
            if 'enero' in line_lower and 'febrero' in line_lower:
                idx_header_meses = i
                break

        if idx_header_meses == -1:
            # No se encontró tabla de meses, retornar vacío
            return []

        # Identificar la posición de cada mes en el header
        header_line = lines[idx_header_meses]
        meses_posiciones = []
        for mes in self.MESES:
            # Buscar posición aproximada del mes en el header
            idx = header_line.lower().find(mes[:3])  # Buscar por primeras 3 letras
            if idx != -1:
                meses_posiciones.append((mes, idx))

        meses_posiciones.sort(key=lambda x: x[1])  # Ordenar por posición

        # Buscar líneas con "Subtotal" después del header
        for i in range(idx_header_meses + 1, len(lines)):
            line = lines[i]
            if 'subtotal' in line.lower():
                # Extraer montos de esta línea
                montos = re.findall(r'(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})', line)

                # Mapear montos a meses (asumiendo mismo orden que header)
                for j, (mes, _) in enumerate(meses_posiciones):
                    if j < len(montos):
                        monto_str = montos[j].replace('.', '').replace(',', '.')
                        try:
                            monto = float(monto_str)
                            if monto > 0:
                                totales_por_mes[mes] += monto
                        except ValueError:
                            continue

        # Convertir a formato de salida
        meses_data = []
        for mes in self.MESES:
            if totales_por_mes[mes] > 0:
                meses_data.append({
                    "mes": mes,
                    "sueldo_bruto": 0,  # No extraemos sueldo del F.572 (usuario lo carga)
                    "deducciones_opcionales_total": round(totales_por_mes[mes], 2)
                })

        return meses_data

    def _extraer_deducciones_detalle(self, text: str) -> Dict[str, float]:
        """
        Extrae el detalle de deducciones por tipo.
        Busca secciones específicas del F.572 y suma los subtotales mensuales.
        """
        deducciones = {}
        lines = text.split('\n')

        # Buscar cada tipo de deducción
        for concepto_f572, tipo_deduccion in self.MAPEO_DEDUCCIONES.items():
            # Buscar la línea que contiene el concepto
            idx_concepto = -1
            for i, line in enumerate(lines):
                if concepto_f572 in line.lower():
                    idx_concepto = i
                    print(f"DEBUG - Encontrado concepto '{concepto_f572}' en línea {i}: {line}")
                    break

            if idx_concepto == -1:
                continue

            # Buscar todas las líneas con "Subtotal:" después del concepto
            # hasta encontrar el siguiente concepto o fin de sección
            total_deduccion = 0.0
            for i in range(idx_concepto + 1, min(idx_concepto + 50, len(lines))):
                line = lines[i]

                # Si encontramos otro concepto, parar
                if any(otro_concepto in line.lower() for otro_concepto in self.MAPEO_DEDUCCIONES.keys() if otro_concepto != concepto_f572):
                    break

                # Buscar líneas con "Subtotal:"
                if 'subtotal:' in line.lower():
                    # Extraer el monto del subtotal
                    montos = re.findall(r'\$\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})', line)
                    if montos:
                        monto_str = montos[0].replace('.', '').replace(',', '.')
                        try:
                            monto = float(monto_str)
                            total_deduccion += monto
                            print(f"DEBUG - Subtotal encontrado: ${monto_str} -> {monto}")
                        except ValueError:
                            continue

            if total_deduccion > 0:
                deducciones[tipo_deduccion] = round(total_deduccion, 2)
                print(f"DEBUG - Total '{tipo_deduccion}': ${total_deduccion}")

        return deducciones

    def aplicar_topes(self, deducciones: Dict[str, float], calculadora) -> Dict[str, float]:
        """
        Aplica los topes legales a las deducciones.
        Si una deducción excede el tope, la limita al máximo permitido.

        Args:
            deducciones: Dict con tipo_deduccion: monto
            calculadora: Instancia de CalculadoraGanancias para obtener topes

        Returns:
            Dict con deducciones ajustadas a los topes
        """
        deducciones_ajustadas = {}

        # Obtener deducciones y topes de la calculadora
        deducciones_config = calculadora.obtener_deducciones()

        for tipo, monto in deducciones.items():
            # Buscar el tope para este tipo de deducción en el dict
            deduccion_config = deducciones_config["deducciones_opcionales"].get(tipo)

            if deduccion_config and "tope_anual" in deduccion_config:
                tope = deduccion_config["tope_anual"]
                # Si excede el tope, limitar
                if monto > tope:
                    deducciones_ajustadas[tipo] = tope
                else:
                    deducciones_ajustadas[tipo] = monto
            else:
                # Sin tope, mantener el monto original
                deducciones_ajustadas[tipo] = monto

        return deducciones_ajustadas
