import psutil
import platform
import datetime
from telegram import Update
from telegram.ext import ContextTypes
from core.security import auth_required

@auth_required
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reporte de estado del sistema (RPi4)"""
    
    # Métricas de Sistema
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    
    # CPU & RAM
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Disco (Root)
    disk = psutil.disk_usage('/')
    
    # Temperatura (Solo funciona en Linux/RPi, try/except para dev en Windows)
    temp_msg = "N/A"
    try:
        temps = psutil.sensors_temperatures()
        if 'cpu_thermal' in temps:
            temp_msg = f"{temps['cpu_thermal'][0].current}°C"
    except Exception:
        temp_msg = "No disponible (Windows/Err)"

    # Red (IP de Tailscale prioritaria)
    ip_tailscale = "No detectada"
    ip_local = "N/A"
    try:
        import socket
        # Buscar interfaces de red
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    if interface == "tailscale0" or addr.address.startswith("100."):
                        ip_tailscale = addr.address
                    elif not addr.address.startswith("127."):
                        ip_local = addr.address
    except Exception:
        pass

    msg = (
        f"🤖 *CENTINELA STATUS REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *IP Tailscale:* `{ip_tailscale}`\n"
        f"🏠 *IP Local:* `{ip_local}`\n"
        f"⏱ *Uptime:* {str(uptime).split('.')[0]}\n"
        f"🌡 *Temp CPU:* {temp_msg}\n"
        f"🧠 *CPU Load:* {cpu_percent}%\n"
        f"💾 *RAM:* {memory.percent}% ({round(memory.used/1024**3, 1)}GB / {round(memory.total/1024**3, 1)}GB)\n"
        f"💿 *Disk:* {disk.percent}% Used\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛡 *Sistema:* {platform.system()} {platform.release()}"
    )

    await update.message.reply_text(msg, parse_mode='Markdown')

@auth_required
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comandos disponibles"""
    msg = (
        "👮‍♂️ *Comandos de Centinela:*\n\n"
        "/status - Ver estado del hardware (CPU, Temp, Disco)\n"
        "/scan - Escanear red en busca de cámaras y sensores\n"
        "/snap - Ver cámara: /snap <IP> <User> <Pass>\n"
        "/ping - Verificar conectividad básica\n"
        "/log - Descargar ultimos logs (WIP)\n"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')
