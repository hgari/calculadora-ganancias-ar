const API_URL = 'http://localhost:8000';
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

async function calcularGanancias() {
    const sueldoBruto = parseFloat(document.getElementById('sueldoBruto').value);
    const estadoCivil = document.getElementById('estadoCivil').value;
    const cantidadHijos = parseInt(document.getElementById('cantidadHijos').value);

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
        deducciones_opcionales: deduccionesOpcionales
    };

    try {
        const response = await fetch(`${API_URL}/calcular`, {
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
        mostrarResultados(resultado);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al calcular. Asegúrate de que el servidor esté ejecutándose en ' + API_URL);
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
        { label: 'Total Mensual', valor: deducciones.total_mensual }
    ];

    items.forEach(item => {
        if (item.label.includes('Cónyuge') && item.valor === 0) return;
        if (item.label.includes('Hijos') && item.valor === 0) return;

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

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const panels = document.querySelectorAll('.panel');
    panels.forEach(panel => panel.classList.remove('show'));

    // Cargar deducciones y topes
    cargarDeducciones();
});
