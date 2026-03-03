import logging
import os
import datetime
import holidays
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config.settings import TELEGRAM_TOKEN, LOG_LEVEL, ALLOWED_USER_ID
from core.security import auth_required
from modules.monitoring import status, help_command
from modules.discovery import scan_network_command
from modules.cameras import get_snapshot_command
from modules.sensors import sensors_status

# Configuración básica de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL,
    handlers=[
        logging.FileHandler("logs/centinela.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Comandos Básicos --- #
@auth_required
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🫡 Centinela activado. A sus órdenes, {user.first_name}.")

@auth_required
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Sistema en línea y seguro.")

from core.sensors import sensor_manager

async def watchdog_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Tarea periódica para chequear alertas críticas.
    Detecta cambios en los sensores (Online/Offline o Apertura/Cierre).
    """
    try:
        changed_sensors = await sensor_manager.update_all()
        if not changed_sensors:
            return
            
        now = datetime.datetime.now()
        is_working_hours = False
        
        # Check if it's weekday (0=Monday, 6=Sunday)
        if now.weekday() < 5:
            ar_holidays = holidays.AR(years=now.year)
            if now.date() not in ar_holidays:
                start_time = datetime.time(8, 0)
                end_time = datetime.time(18, 30)
                if start_time <= now.time() <= end_time:
                    is_working_hours = True
                    
        for sensor in changed_sensors:
            if is_working_hours:
                logger.info(f"Omitiendo alerta para {sensor.name} por horario laboral (Lunes a Viernes de 8:00 a 18:30 no feriado)")
                continue
                
            icon = "🚨" if sensor.status == "online" else "⚠️"
            status_text = "CONECTADO / CERRADO" if sensor.status == "online" else "DESCONECTADO / ABIERTO"
            
            alert_msg = (
                f"{icon} *ALERTA DE SEGURIDAD*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Sujeto: *{sensor.name}*\n"
                f"Estado: `{status_text}`\n"
                f"IP: `{sensor.ip}`"
            )
            
            await context.bot.send_message(
                chat_id=ALLOWED_USER_ID,
                text=alert_msg,
                parse_mode='Markdown'
            )
            logger.info(f"Alerta enviada para {sensor.name}: {sensor.status}")
            
    except Exception as e:
        logger.error(f"Error en watchdog: {e}")

async def post_init(application: ApplicationBuilder):
    """Callback que se ejecuta cuando el bot inicia correctamente."""
    try:
        await application.bot.send_message(
            chat_id=ALLOWED_USER_ID, 
            text="🦅 *Centinela Online*\nSistema iniciado y monitoreando.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"No se pudo enviar mensaje de inicio: {e}")

from telegram.ext import MessageHandler, filters

@auth_required
async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Intercepta los botones legacy (Temperatura, Disco) y devuelve el status"""
    text = update.message.text.lower()
    if "temperatura" in text or "disco" in text or "estado" in text:
        await status(update, context)
    else:
        # Comando desconocido o texto suelto
        pass

def main():
    if not TELEGRAM_TOKEN:
        logger.error("Error: TELEGRAM_TOKEN no encontrado. Revisa tu .env")
        return

    # Crear la aplicación
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("scan", scan_network_command))
    application.add_handler(CommandHandler("snap", get_snapshot_command))
    application.add_handler(CommandHandler("sensors", sensors_status))
    
    # Text handler para botones viejos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))

    # Job Queue (Watchdog) - Requiere python-telegram-bot[job-queue]
    job_queue = application.job_queue
    job_queue.run_repeating(watchdog_job, interval=60, first=10)

    logger.info("🦅 Centinela Bot Iniciado y Escuchando...")
    
    # Run
    application.run_polling()

if __name__ == '__main__':
    main()
