import os
from ssh_tool import upload_file, run_remote_command

host = '100.127.19.45'
user = 'centinela'
pwd = 'Chile5235'

# 1. Create .env files locally
with open('backend.env', 'w') as f:
    f.write('DVR_IP=192.168.1.56\nDVR_USER=centinela\nDVR_PASS=Sanlorenz0\nEZVIZ_USER=admin\nEZVIZ_CODE=NVDDVF\n')

with open('frontend.env', 'w') as f:
    f.write('VITE_API_URL=http://100.127.19.45:8000\n')

with open('bot.env', 'w') as f:
    f.write('TELEGRAM_TOKEN=8492700577:AAFADXegFvwkqJkPyjqEVRv-xbeQCiGmwPU\nALLOWED_USER_ID=591656980\nLOG_LEVEL=INFO\n')

# 2. Upload .env files
upload_file(host, user, pwd, 'backend.env', '/home/centinela/centinela_vm/backend/.env')
upload_file(host, user, pwd, 'frontend.env', '/home/centinela/centinela_vm/frontend/.env')
upload_file(host, user, pwd, 'bot.env', '/home/centinela/centinela_rpi/.env')

# 3. Setup and start services
commands = [
    # Fix cameras.yaml
    "sed -i 's/admin:Sanlorenz0/centinela:Sanlorenz0/g' /home/centinela/centinela_vm/backend/config/cameras.yaml",
    
    # Install backend deps & start
    "cd /home/centinela/centinela_vm/backend && pip3 install -r requirements.txt --break-system-packages",
    "pkill -f 'uvicorn'",
    "cd /home/centinela/centinela_vm/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /home/centinela/backend.log 2>&1 &",
    
    # Install frontend deps & start
    "cd /home/centinela/centinela_vm/frontend && npm install",
    "pkill -f 'vite'",
    "cd /home/centinela/centinela_vm/frontend && nohup npm run dev -- --host 0.0.0.0 > /home/centinela/frontend.log 2>&1 &",
    
    # Install bot deps & start
    "cd /home/centinela/centinela_rpi && pip3 install -r requirements.txt --break-system-packages",
    "pkill -f 'main.py'",
    "cd /home/centinela/centinela_rpi && nohup python3 main.py > /home/centinela/bot.log 2>&1 &"
]

for cmd in commands:
    run_remote_command(host, user, pwd, cmd)

print("Deployment sequence initiated.")
