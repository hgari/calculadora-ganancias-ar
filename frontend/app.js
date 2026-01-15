const API_URL = API_CONFIG?.API_URL || 'http://localhost:8000';
let deduccionesConfig = {};

// Mapeo de deducciones del HTML al JSON del backend
const DEDUCCION_MAPPING = {
    'AlquilerInquilino': 'alquiler_inquilino',
    'AlquilerReli': 'alquiler_reli',
    'MedicinaPrepaga': 'medicina_prepaga',
    'GastosMedicos': 'gastos_medicos',
    'SeguroVida': 'seguro_vida',
    'SeguroRetiro': 'seguro_retiro',
    'GastosEducativos': 'gastos_educativos',
    'ServicioDomestico': 'servicio_domestico',
    'InteresesHipotecarios': 'intereses_hipotecarios',
    'Donaciones': 'donaciones',
    'GastosSepelio': 'gastos_sepelio',
    'ImpuestoDebitoCredito': 'impuesto_debitos_creditos',
    'IndumentariaLaboral': 'indumentaria_laboral'
};

// Cargar deducciones y topes al inicio
async function cargarDeducciones() {
    try {
        const response = await fetch(`${API_URL}/deducciones`);
        deduccionesConfig = await response.json();
        mostrarTopes();
    } catch (error) {
        console.error('Error al cargar deducciones:', error);
    }
}

function mostrarTopes() {
    if (deduccionesConfig.deducciones_opcionales) {
        const opciones = deduccionesConfig.deducciones_opcionales;

        // Alquiler Inquilino
        if (opciones.alquiler_inquilino) {
            document.getElementById('topeAlquilerInquilino').textContent = formatCurrency(opciones.alquiler_inquilino.tope_anual);
        }

        // Seguros
        if (opciones.seguro_vida) {
            document.getElementById('topeSeguroVida').textContent = formatCurrency(opciones.seguro_vida.tope_anual);
        }
        if (opciones.seguro_retiro) {
            document.getElementById('topeSeguroRetiro').textContent = formatCurrency(opciones.seguro_retiro.tope_anual);
        }

        // Gastos Educativos
        if (opciones.gastos_educativos) {
            document.getElementById('topeGastosEducativos').textContent = formatCurrency(opciones.gastos_educativos.tope_anual);
        }

        // Servicio Doméstico
        if (opciones.servicio_domestico) {
            document.getElementById('topeServicioDomestico').textContent = formatCurrency(opciones.servicio_domestico.tope_anual);
        }

        // Intereses Hipotecarios
        if (opciones.intereses_hipotecarios) {
            document.getElementById('topeInteresesHipotecarios').textContent = formatCurrency(opciones.intereses_hipotecarios.tope_anual);
        }

        // Gastos de Sepelio
        if (opciones.gastos_sepelio) {
            document.getElementById('topeGastosSepelio').textContent = formatCurrency(opciones.gastos_sepelio.tope_anual);
        }
    }
}

document.getElementById('calculatorForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await calcularGanancias();
});

// Toggle de deducciones opcionales
document.querySelectorAll('.deduccion-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const deduccionId = this.id.replace('ded', '');
        const group = document.getElementById(`group${deduccionId}`);
        if (this.checked) {
            group.classList.remove('hidden');
        } else {
            group.classList.add('hidden');
            const input = group.querySelector('input[type="number"]');
            if (input) input.value = '';
            // Ocultar advertencia
            const adv = document.getElementById(`adv${deduccionId}`);
            if (adv) adv.classList.add('hidden');
        }
    });
});

// Validación en tiempo real de topes
document.querySelectorAll('.deduccion-input-group input[type="number"]').forEach(input => {
    input.addEventListener('input', function() {
        validarTope(this);
    });
});

function validarTope(input) {
    const deduccionId = input.id.replace('monto', '');
    const advElement = document.getElementById(`adv${deduccionId}`);

    if (!advElement) return;

    const montoMensual = parseFloat(input.value) || 0;
    const montoAnual = montoMensual * 12;

    const configKey = DEDUCCION_MAPPING[deduccionId];
    if (!configKey || !deduccionesConfig.deducciones_opcionales) return;

    const deduccionConfig = deduccionesConfig.deducciones_opcionales[configKey];
    if (!deduccionConfig) return;

    // Calcular el monto deducible según el porcentaje
    const porcentajeDeducible = deduccionConfig.porcentaje_deducible || 1.0;
    const montoDeducibleAnual = montoAnual * porcentajeDeducible;

    // Verificar tope fijo anual
    if (deduccionConfig.tope_anual && deduccionConfig.tope_anual !== null) {
        if (montoDeducibleAnual > deduccionConfig.tope_anual) {
            const exceso = montoDeducibleAnual - deduccionConfig.tope_anual;
            advElement.textContent = `⚠️ Superás el tope anual por ${formatCurrency(exceso)}. Solo se deducirán ${formatCurrency(deduccionConfig.tope_anual)} al año.`;
            advElement.classList.remove('hidden');
        } else {
            advElement.classList.add('hidden');
        }
    }
}

// Helper para fetch con timeout y mensaje de cold start
async function fetchWithTimeout(url, options, timeout = 90000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Timeout: El servidor tardó demasiado en responder');
        }
        throw error;
    }
}

// Mostrar mensaje de "despertando" si es la primera vez
let isFirstRequest = true;
function showWakingMessage() {
    if (!API_URL.includes('render.com')) return null;

    const messageDiv = document.createElement('div');
    messageDiv.id = 'wakingMessage';
    messageDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #1e293b;
        color: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        z-index: 10000;
        text-align: center;
        min-width: 300px;
    `;
    messageDiv.innerHTML = `
        <div style="font-size: 1.2rem; margin-bottom: 1rem;">⏳ Servidor despertando...</div>
        <div style="font-size: 0.9rem; color: #94a3b8;">Esto puede tardar 30-60 segundos la primera vez</div>
    `;
    document.body.appendChild(messageDiv);
    return messageDiv;
}

async function calcularGanancias() {
    const sueldoBruto = parseFloat(document.getElementById('sueldoBruto').value);
    const estadoCivil = document.getElementById('estadoCivil').value;
    const cantidadHijos = parseInt(document.getElementById('cantidadHijos').value);
    const otrasCargas = parseInt(document.getElementById('otrasCargas').value || 0);

    const deduccionesOpcionales = [];

    // Procesar cada deducción marcada
    for (const [htmlId, configKey] of Object.entries(DEDUCCION_MAPPING)) {
        const checkbox = document.getElementById(`ded${htmlId}`);
        if (checkbox && checkbox.checked) {
            const input = document.getElementById(`monto${htmlId}`);
            const monto = parseFloat(input.value);

            if (monto > 0) {
                const deduccionConfig = deduccionesConfig.deducciones_opcionales[configKey];
                const nombre = deduccionConfig ? deduccionConfig.nombre : htmlId;

                deduccionesOpcionales.push({
                    concepto: nombre,
                    monto: monto,
                    tipo: configKey
                });
            }
        }
    }

    const requestData = {
        sueldo_bruto: sueldoBruto,
        estado_civil: estadoCivil,
        cantidad_hijos: cantidadHijos,
        otras_cargas: otrasCargas,
        deducciones_opcionales: deduccionesOpcionales
    };

    let wakingMsg = null;
    if (isFirstRequest) {
        wakingMsg = showWakingMessage();
    }

    try {
        const response = await fetchWithTimeout(`${API_URL}/calcular`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        }, 90000); // 90 segundos de timeout

        if (wakingMsg) {
            wakingMsg.remove();
            isFirstRequest = false;
        }

        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }

        const resultado = await response.json();
        mostrarResultados(resultado);
    } catch (error) {
        if (wakingMsg) wakingMsg.remove();
        console.error('Error:', error);
        alert('Error al calcular: ' + error.message + '\n\nSi el error persiste, el servidor en Render puede estar teniendo problemas. Intentá de nuevo en unos minutos.');
    }
}

function mostrarResultados(data) {
    document.getElementById('resultados').classList.remove('hidden');
    document.getElementById('resultados').scrollIntoView({ behavior: 'smooth', block: 'start' });

    document.getElementById('resSueldoBruto').textContent = formatCurrency(data.sueldo_bruto);
    document.getElementById('resImpuestoMensual').textContent = formatCurrency(data.impuesto.impuesto_mensual);
    document.getElementById('resImpuestoAnual').textContent = formatCurrency(data.impuesto.impuesto_anual);
    document.getElementById('resPorcentaje').textContent = (data.porcentaje_efectivo || 0).toFixed(2) + '%';

    mostrarDeducciones(data.deducciones_personales);

    if (data.deducciones_opcionales && data.deducciones_opcionales.length > 0) {
        mostrarDeduccionesOpcionales(data.deducciones_opcionales);
        document.getElementById('deduccionesOpcionalesSection').style.display = 'block';
    } else {
        document.getElementById('deduccionesOpcionalesSection').style.display = 'none';
    }

    mostrarEscalas(data.impuesto);

    if (data.mensaje) {
        document.getElementById('mensaje').textContent = data.mensaje;
        document.getElementById('mensaje').style.display = 'block';
    } else {
        document.getElementById('mensaje').style.display = 'none';
    }
}

function mostrarDeducciones(deducciones) {
    const container = document.getElementById('detalleDeducciones');
    container.innerHTML = '';

    const items = [
        { label: 'Ganancia No Imponible (mensual)', valor: deducciones.gni_mensual || deducciones.gni },
        { label: 'Deducción Especial (mensual)', valor: deducciones.deduccion_especial_mensual || deducciones.deduccion_especial },
        { label: 'Cónyuge (mensual)', valor: deducciones.conyuge_mensual || deducciones.conyuge },
        { label: 'Hijos (mensual)', valor: deducciones.hijos_mensual || deducciones.hijos },
        { label: 'Otras Personas a Cargo (mensual)', valor: deducciones.otras_cargas_mensual || 0 },
        { label: 'Total Mensual', valor: deducciones.total_mensual }
    ];

    items.forEach(item => {
        if (item.label.includes('Cónyuge') && item.valor === 0) return;
        if (item.label.includes('Hijos') && item.valor === 0) return;
        if (item.label.includes('Otras Personas') && item.valor === 0) return;

        const div = document.createElement('div');
        div.className = 'detalle-item';
        div.innerHTML = `
            <span>${item.label}</span>
            <span>${formatCurrency(item.valor)}</span>
        `;
        container.appendChild(div);
    });
}

function mostrarDeduccionesOpcionales(deducciones) {
    const container = document.getElementById('detalleDeduccionesOpcionales');
    container.innerHTML = '';

    deducciones.forEach(deduccion => {
        const div = document.createElement('div');
        div.className = 'detalle-item';
        div.innerHTML = `
            <span>${deduccion.concepto}</span>
            <span>${formatCurrency(deduccion.monto)}</span>
        `;
        container.appendChild(div);
    });
}

function mostrarEscalas(impuesto) {
    const container = document.getElementById('detalleEscalas');
    container.innerHTML = '';

    const resumenDiv = document.createElement('div');
    resumenDiv.innerHTML = `
        <div class="detalle-item">
            <span>Ganancia Anual Sujeta a Impuesto</span>
            <span>${formatCurrency(impuesto.ganancia_anual)}</span>
        </div>
        <div class="detalle-item">
            <span>Impuesto Anual</span>
            <span>${formatCurrency(impuesto.impuesto_anual)}</span>
        </div>
        <div class="detalle-item">
            <span>Impuesto Mensual (promedio)</span>
            <span>${formatCurrency(impuesto.impuesto_mensual)}</span>
        </div>
    `;
    container.appendChild(resumenDiv);

    if (impuesto.detalle_escalas && impuesto.detalle_escalas.length > 0) {
        const escalasTitle = document.createElement('h4');
        escalasTitle.textContent = 'Tramos aplicados:';
        escalasTitle.style.marginTop = '15px';
        escalasTitle.style.marginBottom = '10px';
        container.appendChild(escalasTitle);

        impuesto.detalle_escalas.forEach(escala => {
            const div = document.createElement('div');
            div.style.marginBottom = '10px';
            div.style.padding = '10px';
            div.style.background = '#f8fafc';
            div.style.borderRadius = '6px';

            const hasta = typeof escala.hasta === 'number'
                ? formatCurrency(escala.hasta)
                : escala.hasta;

            div.innerHTML = `
                <div><strong>Desde ${formatCurrency(escala.desde)} hasta ${hasta}</strong></div>
                <div style="font-size: 0.9rem; color: #64748b;">
                    Alícuota: ${escala.porcentaje}% | Fijo: ${formatCurrency(escala.fijo)}
                </div>
                <div style="font-size: 0.9rem;">
                    Base: ${formatCurrency(escala.base_imponible)} → Impuesto: ${formatCurrency(escala.impuesto_tramo)}
                </div>
            `;
            container.appendChild(div);
        });
    }
}

function toggleAccordion(button) {
    button.classList.toggle('active');
    const panel = button.nextElementSibling;
    panel.classList.toggle('show');
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// ===== NUEVA FUNCIONALIDAD: Meses Anteriores =====

const MESES_NOMBRES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

// Toggle de meses anteriores
document.addEventListener('DOMContentLoaded', () => {
    const checkboxMesesAnteriores = document.getElementById('tieneMesesAnteriores');
    const container = document.getElementById('mesesAnterioresContainer');

    if (checkboxMesesAnteriores) {
        checkboxMesesAnteriores.addEventListener('change', function() {
            if (this.checked) {
                container.classList.remove('hidden');
                // No necesitamos generar tabla, solo mostrar los campos
            } else {
                container.classList.add('hidden');
            }
        });
    }

    // Configurar evento de carga de archivo F.572
    const fileInput = document.getElementById('fileF572');
    if (fileInput) {
        fileInput.addEventListener('change', handleF572Upload);
    }
});

// Ya no necesitamos generar tabla mensual
// function generarTablaMeses() { ... } - REMOVED

function recolectarDatosAcumulados() {
    const checkboxMesesAnteriores = document.getElementById('tieneMesesAnteriores');

    if (!checkboxMesesAnteriores || !checkboxMesesAnteriores.checked) {
        return null;
    }

    const ingresosAcumulados = parseFloat(document.getElementById('ingresosAcumulados')?.value || 0);
    const deduccionesAcumuladas = parseFloat(document.getElementById('deduccionesAcumuladas')?.value || 0);
    const impuestoRetenidoAcumulado = parseFloat(document.getElementById('impuestoRetenidoAcumulado')?.value || 0);

    if (ingresosAcumulados <= 0) {
        return null;
    }

    return {
        ingresos_acumulados: ingresosAcumulados,
        deducciones_acumuladas: deduccionesAcumuladas,
        impuesto_retenido_acumulado: impuestoRetenidoAcumulado
    };
}

async function calcularConDatosAcumulados() {
    const sueldoBruto = parseFloat(document.getElementById('sueldoBruto').value);
    const estadoCivil = document.getElementById('estadoCivil').value;
    const cantidadHijos = parseInt(document.getElementById('cantidadHijos').value);
    const otrasCargas = parseInt(document.getElementById('otrasCargas').value || 0);

    const deduccionesOpcionales = [];

    // Procesar cada deducción marcada (código existente)
    for (const [htmlId, configKey] of Object.entries(DEDUCCION_MAPPING)) {
        const checkbox = document.getElementById(`ded${htmlId}`);
        if (checkbox && checkbox.checked) {
            const input = document.getElementById(`monto${htmlId}`);
            const monto = parseFloat(input.value);

            if (monto > 0) {
                const deduccionConfig = deduccionesConfig.deducciones_opcionales[configKey];
                const nombre = deduccionConfig ? deduccionConfig.nombre : htmlId;

                deduccionesOpcionales.push({
                    concepto: nombre,
                    monto: monto,
                    tipo: configKey
                });
            }
        }
    }

    const datosAcumulados = recolectarDatosAcumulados();
    const mesActualNumero = new Date().getMonth() + 1;

    const requestData = {
        mes_actual: {
            sueldo_bruto: sueldoBruto,
            estado_civil: estadoCivil,
            cantidad_hijos: cantidadHijos,
            otras_cargas: otrasCargas,
            deducciones_opcionales: deduccionesOpcionales
        },
        datos_acumulados: datosAcumulados,
        mes_actual_numero: mesActualNumero
    };

    try {
        const response = await fetch(`${API_URL}/calcular-anual`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }

        const resultado = await response.json();
        mostrarResultadosAnuales(resultado);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al calcular. Asegúrate de que el servidor esté ejecutándose en ' + API_URL);
    }
}

function mostrarResultadosAnuales(data) {
    // Mostrar resultados del mes actual (reutilizar función existente)
    mostrarResultados(data.calculo_mes_actual);

    // Mostrar proyección anual
    const proyeccionSection = document.getElementById('proyeccionAnualSection');
    proyeccionSection.classList.remove('hidden');

    document.getElementById('resImpuestoAnualReal').textContent = formatCurrency(data.impuesto_anual_real);
    document.getElementById('resImpuestoYaRetenido').textContent = formatCurrency(data.impuesto_ya_retenido_estimado);
    document.getElementById('resDiferencia').textContent = formatCurrency(Math.abs(data.diferencia));

    // Configurar colores según el tipo de diferencia
    const diferenciaCard = document.getElementById('diferenciaCard');
    const diferenciaTipo = document.getElementById('resDiferenciaTipo');

    diferenciaCard.classList.remove('a-favor', 'en-contra');
    diferenciaTipo.classList.remove('a-favor', 'en-contra');

    if (data.diferencia_tipo === 'a_favor') {
        diferenciaCard.classList.add('a-favor');
        diferenciaTipo.classList.add('a-favor');
        diferenciaTipo.textContent = `A tu favor (+${data.diferencia_porcentual.toFixed(1)}%)`;
    } else if (data.diferencia_tipo === 'en_contra') {
        diferenciaCard.classList.add('en-contra');
        diferenciaTipo.classList.add('en-contra');
        diferenciaTipo.textContent = `En contra (${data.diferencia_porcentual.toFixed(1)}%)`;
    } else {
        diferenciaTipo.textContent = 'Equilibrado';
    }

    // Sugerencia de ajuste
    document.getElementById('mesesRestantes').textContent = data.meses_restantes;
    document.getElementById('resRetencionSugerida').textContent = formatCurrency(data.retencion_mensual_sugerida);
    document.getElementById('resRetencionActual').textContent = formatCurrency(data.retencion_mensual_actual);

    // Resumen mensual
    mostrarResumenMensual(data.resumen_mensual);
}

function mostrarResumenMensual(resumen) {
    const section = document.getElementById('resumenMensualSection');
    const container = document.getElementById('detalleResumenMensual');

    section.style.display = 'block';
    container.innerHTML = '';

    resumen.forEach(mes => {
        const div = document.createElement('div');
        div.className = `mes-item ${mes.tipo}`;

        let mesNombre = mes.mes;
        if (mes.tipo === 'actual') {
            mesNombre = 'Mes Actual';
        } else if (mes.tipo === 'proyectado') {
            mesNombre = 'Proyección';
        } else {
            mesNombre = mes.mes.charAt(0).toUpperCase() + mes.mes.slice(1);
        }

        div.innerHTML = `
            <span class="mes-nombre">${mesNombre}</span>
            <span class="mes-datos">
                Ganancia: ${formatCurrency(mes.ganancia_neta_sujeta)} →
                Impuesto: ${formatCurrency(mes.impuesto_estimado)}
            </span>
        `;
        container.appendChild(div);
    });
}

// Modificar el submit del formulario para detectar si hay datos acumulados
const formulario = document.getElementById('calculatorForm');
formulario.removeEventListener('submit', calcularGanancias); // Remover listener anterior

formulario.addEventListener('submit', async (e) => {
    e.preventDefault();

    const datosAcumulados = recolectarDatosAcumulados();

    if (datosAcumulados) {
        await calcularConDatosAcumulados();
    } else {
        await calcularGanancias();
        // Ocultar secciones de proyección anual si no hay datos acumulados
        const proyeccionSection = document.getElementById('proyeccionAnualSection');
        const resumenSection = document.getElementById('resumenMensualSection');
        if (proyeccionSection) proyeccionSection.classList.add('hidden');
        if (resumenSection) resumenSection.style.display = 'none';
    }
});

// ===== Manejo de Upload F.572 =====

async function handleF572Upload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Mostrar nombre del archivo
    document.getElementById('fileName').textContent = file.name;

    // Mostrar estado de carga
    const uploadStatus = document.getElementById('uploadStatus');
    uploadStatus.className = 'upload-status loading';
    uploadStatus.textContent = 'Procesando PDF...';
    uploadStatus.classList.remove('hidden');

    // Ocultar topes aplicados anteriores
    document.getElementById('topesAplicados').classList.add('hidden');

    try {
        // Crear FormData y enviar al backend
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8000/upload-f572', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al procesar el PDF');
        }

        const data = await response.json();

        // Cargar las deducciones totales en el campo acumulado
        cargarDeduccionesAcumuladas(data.deducciones_con_topes);

        // Mostrar éxito
        uploadStatus.className = 'upload-status success';
        const totalDeducciones = Object.values(data.deducciones_con_topes).reduce((sum, val) => sum + val, 0);
        uploadStatus.textContent = `✓ PDF procesado correctamente. Total deducciones: ${formatCurrency(totalDeducciones)}`;

        // Mostrar advertencia si los topes fueron excedidos
        if (data.topes_aplicados && data.topes_aplicados.length > 0) {
            mostrarTopesAplicados(data.topes_aplicados);
        }

    } catch (error) {
        uploadStatus.className = 'upload-status error';
        uploadStatus.textContent = `✗ Error: ${error.message}`;
        console.error('Error al procesar F.572:', error);
    }
}

function cargarDeduccionesAcumuladas(deduccionesConTopes) {
    // Sumar todas las deducciones del F.572
    const totalDeducciones = Object.values(deduccionesConTopes).reduce((sum, val) => sum + val, 0);

    // Cargar en el campo de deducciones acumuladas
    const deduccionesInput = document.getElementById('deduccionesAcumuladas');
    if (deduccionesInput) {
        deduccionesInput.value = totalDeducciones.toFixed(2);
    }
}

function mostrarTopesAplicados(topesAplicados) {
    const container = document.getElementById('topesAplicados');

    // Mapeo de tipos de deducciones a nombres legibles
    const nombresDeduccion = {
        'prepaga': 'Cuotas Médico Asistenciales',
        'seguro_vida': 'Seguro de Vida',
        'indumentaria': 'Indumentaria y Equipamiento',
        'educacion': 'Gastos de Educación',
        'alquiler': 'Alquileres',
        'servicio_domestico': 'Servicio Doméstico',
        'credito_hipotecario': 'Intereses Hipotecarios'
    };

    let html = '<h5>⚠ Información sobre deducciones del F.572:</h5>';
    html += '<p class="info-text-small">Las siguientes deducciones excedían el límite anual en el F.572. Esta información es solo referencial - <strong>no se cargan automáticamente en el formulario</strong>.</p>';
    html += '<ul>';

    topesAplicados.forEach(tope => {
        const nombre = nombresDeduccion[tope.tipo] || tope.tipo;
        html += `<li><strong>${nombre}:</strong> Declarado en F.572: ${formatCurrency(tope.monto_original)} | Tope legal: ${formatCurrency(tope.monto_con_tope)} | Exceso: ${formatCurrency(tope.diferencia)}</li>`;
    });

    html += '</ul>';
    html += '<p class="info-text-small"><strong>Recordá:</strong> Ingresá manualmente las deducciones del mes actual en el formulario de arriba.</p>';

    container.innerHTML = html;
    container.classList.remove('hidden');
}

// Función para copiar alias de MercadoPago al portapapeles
function copyAlias() {
    const alias = 'HGARI.MELI';
    const btn = document.getElementById('aliasBtn');

    navigator.clipboard.writeText(alias).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg> Copiado!';
        btn.style.background = '#10b981';
        btn.style.color = 'white';

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    }).catch(err => {
        alert('No se pudo copiar el alias. Copialo manualmente: ' + alias);
    });
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const panels = document.querySelectorAll('.panel');
    panels.forEach(panel => panel.classList.remove('show'));

    // Cargar deducciones y topes
    cargarDeducciones();
});
