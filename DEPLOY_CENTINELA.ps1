# Centinela Bot - Deployment Script
# Usage: ./DEPLOY_CENTINELA.ps1

$RemoteUser = "toto"
$RemoteIP = "100.90.101.54"
$RemotePath = "/home/$RemoteUser/centinela_bot"

Write-Host "📦 Creating deployment package..." -ForegroundColor Cyan
Compress-Archive -Path * -Exclude "centinela_deploy.zip" -DestinationPath ".\centinela_deploy.zip" -Force

Write-Host "🚀 Uploading to $RemoteUser@$RemoteIP..." -ForegroundColor Cyan
Write-Host "Note: You will be asked for your SSH password ($RemotePath)" -ForegroundColor Yellow

# Upload Zip
Write-Host "📡 Sending files..." -ForegroundColor Cyan
scp .\centinela_deploy.zip ${RemoteUser}@${RemoteIP}:/home/${RemoteUser}/centinela_deploy.zip

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ SCP Upload Failed!" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Installing on Remote Pi..." -ForegroundColor Cyan
# Remote commands (Cleaning CRLF for Linux)
$Commands = @(
    "sudo apt-get update && sudo apt-get install -y unzip",
    "mkdir -p $RemotePath",
    "unzip -o ~/centinela_deploy.zip -d $RemotePath",
    "cd $RemotePath",
    "python3 -m venv venv",
    "./venv/bin/pip install -r requirements.txt",
    "chmod +x setup_service.sh",
    "sudo ./setup_service.sh",
    "rm ~/centinela_deploy.zip",
    "echo '✅ Deployment Complete!'"
) -join " && "

ssh -t ${RemoteUser}@${RemoteIP} "$Commands"

Write-Host "Done! If you saw 'Deployment Complete', the bot is starting." -ForegroundColor Green
Remove-Item ".\centinela_deploy.zip"
