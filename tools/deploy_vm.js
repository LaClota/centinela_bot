const fs = require('fs');
const { Client } = require('ssh2');
const path = require('path');
const { exec } = require('child_process');

// Parse the VM_ACCESS_TEMPLATE.txt file manually since it's not a standard .env
function getCredentials() {
    try {
        const content = fs.readFileSync(path.join(__dirname, '../VM_ACCESS_TEMPLATE.txt'), 'utf8');
        const config = {};
        content.split('\n').forEach(line => {
            if (line.includes('=')) {
                const [key, value] = line.split('=');
                if (key && value) {
                    config[key.trim()] = value.trim();
                }
            }
        });
        return config;
    } catch (err) {
        console.error("Error reading credentials:", err);
        process.exit(1);
    }
}

const config = getCredentials();
const conn = new Client();

const VM_IP = config.VM_IP;
const VM_USER = config.SSH_USER;
const VM_PASS = config.SSH_PASS;
const VM_PORT = parseInt(config.SSH_PORT) || 22;
const REMOTE_DIR = `/home/${VM_USER}/centinela_vm`;
const TAR_FILE = 'centinela_vm.tar';

console.log(`🚀 Deploying to ${VM_USER}@${VM_IP}...`);

// 1. Create Tarball locally
console.log("📦 Creating tarball...");
exec(`tar --exclude='node_modules' --exclude='.venv' --exclude='dist' -cvf ${TAR_FILE} centinela_vm`, { cwd: path.join(__dirname, '..') }, (err, stdout, stderr) => {
    if (err) {
        console.error("Error creating tarball:", stderr);
        return;
    }

    // 2. Connect and Upload
    conn.on('ready', () => {
        console.log('✅ SSH Connection established');

        conn.sftp((err, sftp) => {
            if (err) throw err;

            const localTarPath = path.join(__dirname, '..', TAR_FILE);
            const remoteTarPath = `/home/${VM_USER}/${TAR_FILE}`;

            console.log("📤 Uploading tarball...");
            sftp.fastPut(localTarPath, remoteTarPath, (err) => {
                if (err) throw err;
                console.log("✅ Upload successful");

                // 3. Extract and Cleanup
                const commands = [
                    `mkdir -p ${REMOTE_DIR}`,
                    `tar -xvf ${remoteTarPath} -C /home/${VM_USER}`, // Extract to home, it will create/overwrite centinela_vm dir
                    `rm ${remoteTarPath}`,
                    `echo "🎉 Deployment Complete!"`,
                    `ls -la ${REMOTE_DIR}`
                ];

                conn.exec(commands.join(' && '), (err, stream) => {
                    if (err) throw err;
                    stream.on('close', (code, signal) => {
                        console.log('Stream :: close :: code: ' + code + ', signal: ' + signal);
                        conn.end();
                        // Cleanup local tar
                        fs.unlinkSync(localTarPath);
                    }).on('data', (data) => {
                        console.log('STDOUT: ' + data);
                    }).stderr.on('data', (data) => {
                        console.log('STDERR: ' + data);
                    });
                });
            });
        });
    }).connect({
        host: VM_IP,
        port: VM_PORT,
        username: VM_USER,
        password: VM_PASS,
        readyTimeout: 20000 // Increase timeout
    });
});
