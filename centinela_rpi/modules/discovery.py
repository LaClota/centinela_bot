import logging
import asyncio
from scapy.all import ARP, Ether, srp
import socket
from telegram import Update
from telegram.ext import ContextTypes
from core.security import auth_required

logger = logging.getLogger(__name__)

# Base de datos simplificada de OUI (Fabricantes)
# En un futuro esto podría estar en un archivo aparte o usar una librería 'mac-vendor-lookup'
VENDOR_OUI = {
    "Hikvision": ["10:12:FB", "4C:BD:8F", "A4:14:37", "C4:2F:90"],
    "Ezviz": ["2C:A5:39", "70:B1:05"], # A veces comparten OUI con Hikvision
    "Espressif": ["24:0A:C4", "30:AE:A4", "3C:71:BF", "54:43:B2", "60:01:94", "84:F3:EB", "AC:D0:74"],
    "Raspberry Pi": ["B8:27:EB", "DC:A6:32", "E4:5F:01"]
}

class NetworkScanner:
    def __init__(self, ip_range="192.168.1.0/24"):
        self.ip_range = ip_range

    def get_vendor(self, mac):
        mac_prefix = mac.upper()[:8] # XX:XX:XX
        for vendor, ouis in VENDOR_OUI.items():
            # Chequeo simple, en prod ideal usar librerías completas
            for oui in ouis:
                if mac_prefix.startswith(oui):
                    return vendor
        return "Desconocido"

    def scan(self):
        """Ejecuta escaneo ARP (bloqueante, ejecutar en hilo aparte o executor)"""
        logger.info(f"Escaneando red {self.ip_range}...")
        arp = ARP(pdst=self.ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        result = srp(packet, timeout=2, verbose=0)[0]
        devices = []

        for sent, received in result:
            vendor = self.get_vendor(received.hwsrc)
            devices.append({
                'ip': received.psrc,
                'mac': received.hwsrc,
                'vendor': vendor
            })
        
        return devices

scanner = NetworkScanner()

@auth_required
async def scan_network_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /scan para buscar dispositivos en la red"""
    status_msg = await update.message.reply_text("📡 Escaneando red local... (esto toma unos segundos)")
    
    # Ejecutar escaneo en un hilo aparte para no bloquear el bot
    loop = asyncio.get_running_loop()
    try:
        # Detectar la subred local automáticamente
        import socket
        import psutil
        target_network = "192.168.1.0/24" # Default
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127.") and not addr.address.startswith("100."):
                    # Intento simple de obtener la red (asumiendo /24)
                    base_ip = ".".join(addr.address.split(".")[:-1])
                    target_network = f"{base_ip}.0/24"
                    break
        
        scanner.ip_range = target_network
        devices = await loop.run_in_executor(None, scanner.scan)
        
        if not devices:
            await status_msg.edit_text(f"❌ No se encontraron dispositivos en {target_network}.\n(Asegurate de correr el bot con sudo para escaneo ARP)")
            return

        msg = "🔍 *Resultados del Escaneo:*\n\n"
        for dev in devices:
            icon = "❓"
            if dev['vendor'] == "Hikvision" or dev['vendor'] == "Ezviz":
                icon = "📹"
            elif dev['vendor'] == "Espressif":
                icon = "🔌"
            elif dev['vendor'] == "Raspberry Pi":
                icon = "🍓"

            msg += f"{icon} *{dev['ip']}* - {dev['vendor']}\n`{dev['mac']}`\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error en scan: {e}")
        await status_msg.edit_text(f"⚠️ Error al escanear: {str(e)}")
