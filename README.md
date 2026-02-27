# 🦅 SISTEMA CENTINELA - SECURITY SUITE

Una solución de seguridad integral distribuida entre un servidor de procesamiento potente (VM) y una unidad de respaldo crítica (Raspberry Pi).

## 🏗 Arquitectura del Sistema

### 1. 🧠 Centinela VM (El Cerebro)
Ubicación: `/centinela_vm`
Encargado del procesamiento pesado, análisis de video profundo y la interfaz de usuario principal.

*   **Backend (`centinela_vm/backend`):**
    *   **Tecnología:** Python (FastAPI), OpenCV, Ultralytics YOLOv8.
    *   **Funciones:**
        *   Ingesta de streams RTSP (Hikvision, Ezviz).
        *   Detección de personas/objetos en tiempo real.
        *   Reconocimiento facial (Control de personal).
        *   API REST para el frontend.
*   **Frontend (`centinela_vm/frontend`):**
    *   **Tecnología:** React (Vite), CSS Moderno (Glassmorphism).
    *   **Funciones:**
        *   Dashboard de monitoreo en vivo (Grid de cámaras).
        *   Historial de eventos y alertas.
        *   Estado del sistema.

### 2. ❤️ Centinela RPi (El Corazón / Respaldo)
Ubicación: `/centinela_rpi`
Unidad de alta disponibilidad con respaldo de batería. Asegura que el sistema siga vivo incluso si el servidor principal falla.

*   **Core (`centinela_rpi`):**
    *   **Tecnología:** Python.
    *   **Funciones:**
        *   **Telegram Bot:** Interfaz de chat siempre activa (`/status`, `/foto`, alertas).
        *   **Gestor de Sensores:** Lectura directa de GPIO/WiFi (Movimiento, Apertura).
        *   **Modo Emergencia:** Si la VM no responde (ping fallback), captura snapshots básicos de las cámaras y alerta por Telegram.
        *   **Control de Sirenas:** Activación física de alarmas.

## 🚀 Instalación y Despliegue

### VM (Debian 12)
1.  **Backend:**
    ```bash
    cd centinela_vm/backend
    pip install -r requirements.txt
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
2.  **Frontend:**
    ```bash
    cd centinela_vm/frontend
    npm install
    npm run dev
    ```

### Raspberry Pi 4
1.  **Servicio:**
    ```bash
    cd centinela_rpi
    pip install -r requirements.txt
    python main.py
    ```

## 📝 Configuración
Crea un archivo `.env` en cada directorio basado en los `.env.example` proporcionados.
