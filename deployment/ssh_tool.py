import paramiko
import sys
import os

def run_remote_command(host, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        
        # Write directly to files to avoid Windows console unicode errors
        with open('remote_stdout.txt', 'wb') as f:
            f.write(stdout.read())
        with open('remote_stderr.txt', 'wb') as f:
            f.write(stderr.read())
            
        print(f"Exit status: {exit_status}, output saved to remote_stdout.txt")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

def download_file(host, user, password, remote_path, local_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password)
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    except Exception as e:
        print(f"Download failed: {e}")
    finally:
        client.close()

def upload_file(host, user, password, local_path, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password)
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    except Exception as e:
        print(f"Upload failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    action = sys.argv[1]
    host = '100.127.19.45'
    user = 'centinela'
    pwd = 'Chile5235'
    
    if action == "cmd":
        run_remote_command(host, user, pwd, sys.argv[2])
    elif action == "get":
        download_file(host, user, pwd, sys.argv[2], sys.argv[3])
    elif action == "put":
        upload_file(host, user, pwd, sys.argv[2], sys.argv[3])
