import logging
import asyncio
from scapy.all import ARP, Ether, srp
import socket
from telegram import Update
from telegram.ext import ContextTypes
from core.security import auth_required
from mac_vendor_lookup import MacLookup

logger = logging.getLogger(__name__)

# Diccionario de dispositivos conocidos por el usuario (MAC Address en mayúsculas)
KNOWN_DEVICES = {
    "2C:96:82:5D:2C:0A": "Router / Gateway",
    "F8:17:2D:B0:80:BC": "Interruptor Luz Recepción",
    "EC:94:CB:80:8D:AB": "Interruptor Sirena",
    "F8:17:2D:C8:22:89": "Interruptor Luz Ofi Mumi",
    "F8:17:2D:C3:C3:0A": "Interruptor Luz Portón",
    "F8:17:2D:B7:72:56": "Interruptor Luz Entrada",
    "F8:17:2D:B1:3B:9D": "Interruptor Ofi Javi",
    "E0:BA:AD:C0:A1:DD": "DVR Hikvision",
    "EC:94:CB:80:8C:40": "Interruptor Luz Alarma",
    "2E:87:BA:30:BB:01": "Impresora Xerox",
    
    # Sensores a batería (difíciles de ver con Ping/ARP porque duermen)
    "A8:80:55:DE:73:E8": "Sensor Apertura Puerta",
    "18:DE:50:B0:51:7C": "Sensor Mov Ofi Javi",
    "18:DE:50:B0:3C:88": "Sensor Mov Pasillo Portón",
}

class NetworkScanner:
    def __init__(self, ip_range="192.168.1.0/24"):
        self.ip_range = ip_range
        self.mac_lookup = MacLookup()
        try:
            self.mac_lookup.update_vendors()
        except Exception as e:
            logger.error(f"Error actualizando vendor OUI en inicialización: {e}")

    def get_vendor(self, mac):
        try:
            vendor = self.mac_lookup.lookup(mac)
            if "," in vendor:
                vendor = vendor.split(",")[0]
            if " " in vendor and len(vendor) > 15:
                vendor = vendor.split(" ")[0]
            return vendor
        except Exception:
            return "Fabr. Desconocido"

    def scan(self):
        """Ejecuta escaneo ARP (bloqueante, ejecutar en hilo aparte o executor)"""
        logger.info(f"Escaneando red {self.ip_range}...")
        arp = ARP(pdst=self.ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        result = srp(packet, timeout=3, verbose=0)[0]
        devices = []

        for sent, received in result:
            mac_upper = received.hwsrc.upper()
            
            # 1. Chequeamos si es un dispositivo conocido
            custom_name = KNOWN_DEVICES.get(mac_upper)
            
            # 2. Obtenemos el fabricante real
            vendor = self.get_vendor(received.hwsrc)
            
            name_to_display = f"{custom_name} ({vendor})" if custom_name else vendor

            devices.append({
                'ip': received.psrc,
                'mac': received.hwsrc,
                'name': name_to_display,
                'is_known': bool(custom_name)
            })
        
        # Ordenar por IP (simplificado)
        devices.sort(key=lambda x: [int(p) for p in x['ip'].split('.')])
        return devices

scanner = NetworkScanner()

@auth_required
async def scan_network_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /scan para buscar dispositivos en la red"""
    status_msg = await update.message.reply_text("📡 Escaneando red local...")
    
    loop = asyncio.get_running_loop()
    try:
        import socket
        import psutil
        target_network = "192.168.1.0/24"
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127.") and not addr.address.startswith("100."):
                    base_ip = ".".join(addr.address.split(".")[:-1])
                    target_network = f"{base_ip}.0/24"
                    break
        
        scanner.ip_range = target_network
        devices = await loop.run_in_executor(None, scanner.scan)
        
        if not devices:
            await status_msg.edit_text(f"❌ No se encontraron dispositivos en {target_network}.")
            return

        msg = "🔍 *Escaneo de Red:*\n\n"
        for dev in devices:
            icon = "🏷️" if dev['is_known'] else "❓"
            
            if not dev['is_known']:
                if "Hikvision" in dev['name'] or "Ezviz" in dev['name']:
                    icon = "📹"
                elif "Espressif" in dev['name'] or "Tuya" in dev['name']:
                    icon = "🔌"

            msg += f"{icon} *{dev['ip']}* - {dev['name']}\n`{dev['mac']}`\n"
        
        await status_msg.edit_text(msg, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error en scan: {e}")
        await status_msg.edit_text(f"⚠️ Error al escanear: {str(e)}")
