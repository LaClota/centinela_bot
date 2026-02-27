import os
import logging
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Configuración del Bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", 0))

# Configuración de Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join("logs", "centinela.log")

# Validaciones básicas
if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "CHANGE_ME":
    raise ValueError("El TELEGRAM_TOKEN no está configurado en el archivo .env")

if not ALLOWED_USER_ID or ALLOWED_USER_ID == "CHANGE_ME":
    logging.warning("El ALLOWED_USER_ID no está configurado. El bot podría no responder a nadie.")
