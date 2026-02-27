import cv2
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from core.security import auth_required

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self):
        # En el futuro, esto podría cargarse de una DB o config
        # Formato: { "alias": {"ip": "192.168.1.X", "user": "admin", "pass": "12345"} }
        self.cameras = {} 

    def get_rtsp_url(self, ip, user="admin", password="password123"):
        # URL genérica para Hikvision/Ezviz
        # Main stream: /Streaming/Channels/101
        # Sub stream: /Streaming/Channels/102
        return f"rtsp://{user}:{password}@{ip}:554/Streaming/Channels/101"

    def capture_snapshot(self, ip, user, password):
        """Captura un frame usando OpenCV y RTSP"""
        rtsp_url = self.get_rtsp_url(ip, user, password)
        logger.info(f"Intentando capturar de: {rtsp_url.replace(password, '******')}")
        
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            logger.error(f"No se pudo conectar a {ip}")
            return None

        # Leer un frame
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Guardar temporalmente
            filename = f"temp_snap_{ip.replace('.', '_')}.jpg"
            cv2.imwrite(filename, frame)
            return filename
        else:
            return None

camera_manager = CameraManager()

@auth_required
async def get_snapshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Uso: /snap <IP> <USER> <PASS>
    Ejemplo: /snap 192.168.1.64 admin admin123
    """
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("📸 Uso: `/snap <IP> <USER> <PASSWORD>`", parse_mode='Markdown')
        return

    ip = args[0]
    user = args[1]
    password = args[2]

    status_msg = await update.message.reply_text(f"📸 Conectando a cámara {ip}...")

    # Ejecutar OpenCV en hilo aparte (bloqueante)
    loop = asyncio.get_running_loop()
    try:
        photo_path = await loop.run_in_executor(None, camera_manager.capture_snapshot, ip, user, password)
        
        if photo_path:
            await update.message.reply_photo(photo=open(photo_path, 'rb'), caption=f"📡 Vista previa de {ip}")
            os.remove(photo_path) # Limpiar archivo
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Error al capturar imagen. ¿IP/Credenciales correctas? ¿RTSP habilitado?")

    except Exception as e:
        logger.error(f"Error snap: {e}")
        await status_msg.edit_text(f"⚠️ Excepción: {e}")
