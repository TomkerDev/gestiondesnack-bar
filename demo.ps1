#Requires -Version 5.1
<#
  DEMO Snack-bar — lance tout pour la presentation client.
  - Serveur local (back) sur http://127.0.0.1:8080  (API + front statique)
  - Front dev (Vite/SvelteKit) sur http://localhost:5173 (proxy /api -> 8080)
  Usage : clic droit > Executer avec PowerShell  (ou : powershell -ExecutionPolicy Bypass -File demo.ps1)
#>
$ErrorActionPreference = "Stop"
$Racine = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Racine

Write-Host ""
Write-Host "  === DEMO Snack-bar ===" -ForegroundColor Cyan
Write-Host ""

# 1. Dependances front (si dossier manquant)
if (-not (Test-Path "$Racine/app/node_modules/vite/package.json")) {
  Write-Host "[1/4] Installation des dependances front (npm install)..." -ForegroundColor Yellow
  Push-Location "$Racine/app"; npm install --no-audit --no-fund; Pop-Location
} else {
  Write-Host "[1/4] Dependances front OK." -ForegroundColor Green
}

# 2. Build front frais (le serveur sert app/build)
Write-Host "[2/4] Build du front..." -ForegroundColor Yellow
Push-Location "$Racine/app"; npm run build | Select-Object -Last 2; Pop-Location
if (-not (Test-Path "$Racine/app/build/index.html")) { throw "Echec du build front." }
Write-Host "      Build OK." -ForegroundColor Green

# 3. Serveur local (fond, une seule instance)
Write-Host "[3/4] Demarrage du serveur (port 8080)..." -ForegroundColor Yellow
# NB : sur certaines installs le binaire est python3.13.exe (pas python.exe) :
# un filtre Win32_Process sur 'python.exe' ne trouverait RIEN et l'ancien serveur
# garderait le port 8080 en servant du code perime. On filtre donc sur la ligne
# de commande, tous binaires python confondus.
$existant = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like "python*" -and $_.CommandLine -like "*serveur*serveur.py*" }
foreach ($p in $existant) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
# Filet de securite : libere le port si un processus l'occupe encore
Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
Start-Sleep -Milliseconds 400
Start-Process python -ArgumentList "`"$Racine/serveur/serveur.py`"","8080" `
  -WorkingDirectory $Racine -WindowStyle Minimized
for ($i = 0; $i -lt 50; $i++) {
  try { (New-Object Net.WebClient).DownloadString("http://127.0.0.1:8080/api/produits") | Out-Null; break }
  catch { Start-Sleep -Milliseconds 200 }
}
Write-Host "      Serveur OK : http://127.0.0.1:8080" -ForegroundColor Green

# 4. Front dev (fond)
Write-Host "[4/4] Demarrage du front (port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$Racine/app'; npm run dev -- --port 5173 --host 127.0.0.1" `
  -WorkingDirectory "$Racine/app" -WindowStyle Minimized
Start-Sleep -Seconds 6

Write-Host ""
Write-Host "  DEMO PRETE :" -ForegroundColor Cyan
Write-Host "    Client (dev)  : http://localhost:5173" -ForegroundColor White
Write-Host "    Serveur (API) : http://127.0.0.1:8080/api/produits" -ForegroundColor White
Write-Host ""
Write-Host "  Codes de demo : Awa=1234 (serveur) | Moussa=2222 | Ibrahim=9111 (gerant) | Hassane=9999 (proprio)" -ForegroundColor DarkGray
Write-Host "  Arret : Get-Process python,node -ErrorAction SilentlyContinue | Stop-Process" -ForegroundColor DarkGray
Write-Host ""
Start-Process "http://localhost:5173"
