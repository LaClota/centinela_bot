#!/bin/bash
# setup_service.sh - Configura Systemd para arranque automático

SERVICE_FILE="/etc/systemd/system/centinela.service"
USER=$(whoami)
DIR="/home/$USER/centinela_bot"
PYTHON="$DIR/venv/bin/python"

echo "🔧 Configurando Centinela como Servicio..."

# Confirmar rutas
if [ ! -f "$PYTHON" ]; then
    echo "❌ Error: No se encuentra el entorno virtual en $PYTHON"
    echo "  -> Ejecuta primero: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Crear archivo de servicio
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Centinela Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=$PYTHON $DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Archivo de servicio creado en $SERVICE_FILE"

# Recargar daemon y habilitar
sudo systemctl daemon-reload
sudo systemctl enable centinela
sudo systemctl start centinela

echo "🚀 Servicio iniciado y habilitado para arranque automático."
echo "📋 Estado actual:"
sudo systemctl status centinela --no-pager
