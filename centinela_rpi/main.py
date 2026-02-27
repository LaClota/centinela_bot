import logging
import os
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

# --- Watchdog (Background Task placeholder) --- #
async def watchdog_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Tarea periódica para chequear alertas críticas.
    Aquí iría la lógica de revisar sensores GPIO o alertas de cámaras.
    """
    # Ejemplo: Si la temperatura sube de X, mandar alerta.
    # Por ahora es solo un placeholder silencioso.
    pass

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

    # Job Queue (Watchdog) - Requiere python-telegram-bot[job-queue]
    job_queue = application.job_queue
    job_queue.run_repeating(watchdog_job, interval=60, first=10)

    logger.info("🦅 Centinela Bot Iniciado y Escuchando...")
    
    # Run
    application.run_polling()

if __name__ == '__main__':
    main()
