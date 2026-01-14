// Configuración de la URL del API
// Para desarrollo local: 'http://localhost:8000'
// Para producción: URL de tu backend en Render

const API_CONFIG = {
    // Detectar automáticamente el entorno
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://calculadora-ganancias-backend.onrender.com'  // Cambiá esto por tu URL de Render
};

// Si necesitás una URL específica para desarrollo local en red:
// API_CONFIG.API_URL = 'http://TU_IP:8000';  // Ejemplo: 'http://192.168.1.100:8000'
