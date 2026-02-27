from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging
import os

# Cargar settings si es necesario, o usar os.getenv directamente si este módulo se importa antes
from config.settings import ALLOWED_USER_ID

logger = logging.getLogger(__name__)

def auth_required(func):
    """
    Decorador de seguridad:
    1. Verifica que el User ID coincida con el dueño (ALLOWED_USER_ID).
    2. (Opcional) Se podría validar idioma aquí, pero el ID es el bloqueo fuerte.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return # No es un usuario (puede ser update de canal, etc.)

        if user.id != ALLOWED_USER_ID:
            logger.warning(f"⛔ Acceso NO AUTORIZADO intentado por usuario: {user.full_name} (ID: {user.id})")
            # Silenciosamente ignorar, o responder algo genérico si se prefiere.
            # Por seguridad (stealth), mejor no responder nada a extraños.
            return 

        return await func(update, context, *args, **kwargs)
    return wrapper
