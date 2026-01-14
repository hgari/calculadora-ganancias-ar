// Configuración de la URL del API
// Para desarrollo local: 'http://localhost:8000'
// Para producción: 'https://tu-servidor.com/api' o la URL de tu backend

const API_CONFIG = {
    // Detectar automáticamente si estamos en localhost o no
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : `${window.location.protocol}//${window.location.hostname}:8000`
};

// Si necesitás una URL específica, descomentá y configurá esta línea:
// API_CONFIG.API_URL = 'http://TU_IP:8000';  // Ejemplo: 'http://192.168.1.100:8000'
