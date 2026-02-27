const fs = require('fs');
const { Client } = require('ssh2');
const path = require('path');

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
const cmd = process.argv.slice(2).join(' ');

if (!cmd) {
    console.error("Please provide a command to execute");
    process.exit(1);
}

const RPI_IP = config.TARGET_IP;
const RPI_USER = config.SSH_USER;
const RPI_PASS = config.SSH_PASS;
const RPI_PORT = parseInt(config.SSH_PORT) || 22;

console.log(`🚀 Executing on ${RPI_USER}@${RPI_IP}: "${cmd}"`);

conn.on('ready', () => {
    console.log('✅ Connected');
    conn.exec(cmd, (err, stream) => {
        if (err) throw err;
        stream.on('close', (code, signal) => {
            console.log('Stream :: close :: code: ' + code + ', signal: ' + signal);
            conn.end();
        }).on('data', (data) => {
            console.log('STDOUT: ' + data);
        }).stderr.on('data', (data) => {
            console.log('STDERR: ' + data);
        });
    });
}).connect({
    host: RPI_IP,
    port: RPI_PORT,
    username: RPI_USER,
    password: RPI_PASS,
    readyTimeout: 20000
});
