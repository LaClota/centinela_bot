import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
import subprocess
from core.security import auth_required

logger = logging.getLogger(__name__)

# Configuración Temporal de Sensores (Idealmente mover a config/sensors.yaml)
SENSORS = [
    {"name": "Sensor Tuya/Wifi", "ip": "192.168.1.32", "type": "ping"},
    {"name": "Espressif Device", "ip": "192.168.1.58", "type": "ping"},
    {"name": "Hikvision DVR",    "ip": "192.168.1.56", "type": "ping"},
    {"name": "Ezviz Camera",     "ip": "192.168.1.38", "type": "ping"},
    {"name": "VM Backend",       "ip": "192.168.1.48", "type": "ping"}
]

async def check_ping(ip):
    try:
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', ip, 
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0
    except Exception as e:
        logger.error(f"Error pinging {ip}: {e}")
        return False

@auth_required
async def sensors_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver estado de los sensores y dispositivos conocidos"""
    status_msg = "📡 *Estado de Red de Sensores*\n"
    status_msg += "━━━━━━━━━━━━━━━━━━━━\n"
    
    tasks = [check_ping(s['ip']) for s in SENSORS]
    results = await asyncio.gather(*tasks)
    
    for sensor, is_online in zip(SENSORS, results):
        icon = "✅" if is_online else "🔴"
        status_msg += f"{icon} *{sensor['name']}*\n    `{sensor['ip']}`\n"
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')
