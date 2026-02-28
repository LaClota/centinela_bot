import paramiko
import sys
import time

host = '100.127.19.45'
user = 'centinela'
pwd = 'Chile5235'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print(f"Connecting to {host}...")
    client.connect(host, username=user, password=pwd)
    
    cmd = "curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/ns.sh && echo 'Chile5235' | sudo -S bash /tmp/ns.sh && echo 'Chile5235' | sudo -S apt-get install -y nodejs"
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            sys.stdout.write(stdout.channel.recv(1024).decode('utf-8'))
        if stderr.channel.recv_stderr_ready():
            sys.stderr.write(stderr.channel.recv_stderr(1024).decode('utf-8'))
        time.sleep(1)
        
    print(f"\nExit status: {stdout.channel.recv_exit_status()}")
except Exception as e:
    print(f"Failed: {e}")
finally:
    client.close()
