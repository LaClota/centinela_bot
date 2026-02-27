#!/bin/bash
# setup_brain.sh - Configura el servicio del Cerebro (Backend) en systemd

SERVICE_NAME="centinela-backend"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
SOURCE_SERVICE_FILE="centinela-backend.service"

echo "🔧 Configurando Centinela Brain (Backend) como Servicio..."

# Verificar que el archivo de servicio existe en el repo
if [ ! -f "$SOURCE_SERVICE_FILE" ]; then
    echo "❌ Error: No se encuentra $SOURCE_SERVICE_FILE en el directorio actual."
    exit 1
fi

# Copiar archivo al sistema
echo "📡 Copiando archivo de servicio a $SERVICE_FILE..."
sudo cp "$SOURCE_SERVICE_FILE" "$SERVICE_FILE"

# Recargar daemon y habilitar
echo "🔄 Recargando systemd y habilitando servicio..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Servicio $SERVICE_NAME configurado e iniciado."
echo "📋 Estado actual:"
sudo systemctl status "$SERVICE_NAME" --no-pager
