const fs = require('fs');
const { Client } = require('ssh2');
const path = require('path');
const { exec } = require('child_process');

function getCredentials() {
    try {
        const content = fs.readFileSync(path.join(__dirname, '../REMOTE_ACCESS_TEMPLATE.txt'), 'utf8');
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
const TAR_FILE = 'centinela_rpi.tar';

const RPI_IP = config.TARGET_IP;
const RPI_USER = config.SSH_USER;
const RPI_PASS = config.SSH_PASS;
const RPI_PORT = parseInt(config.SSH_PORT) || 22;
const TARGET_DIR = '/home/toto/centinela_rpi';

console.log(`🚀 Deploying RPi to ${RPI_USER}@${RPI_IP}...`);

// 1. Create Tarball locally (Exclude venv and pycache)
console.log("📦 Creating tarball...");
exec(`tar --exclude='venv' --exclude='__pycache__' --exclude='.git' -cvf ${TAR_FILE} centinela_rpi`, { cwd: path.join(__dirname, '..') }, (err, stdout, stderr) => {
    if (err) {
        console.error("Error creating tarball:", stderr);
        return;
    }

    // 2. Connect via SSH
    conn.on('ready', () => {
        console.log('✅ SSH Connection established');

        // 3. Upload Tarball
        console.log("📤 Uploading tarball...");
        conn.sftp((err, sftp) => {
            if (err) throw err;

            sftp.fastPut(path.join(__dirname, '..', TAR_FILE), `/home/${RPI_USER}/${TAR_FILE}`, (err) => {
                if (err) throw err;
                console.log("✅ Upload complete");

                // 4. Extract and Setup
                console.log("🔧 Extracting and setting up...");
                const commands = [
                    `mkdir -p ${TARGET_DIR}`,
                    `tar -xvf ${TAR_FILE} -C /home/${RPI_USER}/`, // Extracts into /home/toto/centinela_rpi because tar includes the dir
                    `rm ${TAR_FILE}`,
                    `cd ${TARGET_DIR}`,
                    `python3 -m venv venv`,
                    `venv/bin/pip install -r requirements.txt`
                ];

                conn.exec(commands.join(' && '), (err, stream) => {
                    if (err) throw err;
                    stream.on('close', (code, signal) => {
                        console.log('📜 Setup complete. Code: ' + code);
                        conn.end();
                        // Cleanup local tar
                        fs.unlinkSync(path.join(__dirname, '..', TAR_FILE));
                    }).on('data', (data) => {
                        console.log('STDOUT: ' + data);
                    }).stderr.on('data', (data) => {
                        console.log('STDERR: ' + data);
                    });
                });
            });
        });

    }).connect({
        host: RPI_IP,
        port: RPI_PORT,
        username: RPI_USER,
        password: RPI_PASS,
        readyTimeout: 20000
    });
});
