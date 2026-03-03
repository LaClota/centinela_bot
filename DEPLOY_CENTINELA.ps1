# Centinela Bot - Deployment Script
$RemoteUser = "centinela"
$RemoteIP = "100.119.235.64"
$RemotePath = "/home/$RemoteUser/centinela_bot"

Write-Host "Creating deployment package..." -ForegroundColor Cyan
Get-ChildItem -Path * -Exclude "centinela_deploy.zip" | Compress-Archive -DestinationPath ".\centinela_deploy.zip" -Force

Write-Host "Uploading to $RemoteUser@$RemoteIP..." -ForegroundColor Cyan
scp .\centinela_deploy.zip ${RemoteUser}@${RemoteIP}:/home/${RemoteUser}/centinela_deploy.zip
if ($LASTEXITCODE -ne 0) { exit 1 }

$Commands = 'sudo apt-get update ; sudo apt-get install -y unzip ; mkdir -p ' + $RemotePath + ' ; unzip -o ~/centinela_deploy.zip -d ' + $RemotePath + ' ; cd ' + $RemotePath + ' ; python3 -m venv venv ; ./venv/bin/pip install -r requirements.txt ; chmod +x setup_service.sh ; sudo ./setup_service.sh ; rm ~/centinela_deploy.zip ; echo "[OK] Deployment Complete!"'
ssh -t ${RemoteUser}@${RemoteIP} "$Commands"
Remove-Item ".\centinela_deploy.zip"
