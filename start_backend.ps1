Write-Host "Starting Credit Memo Backend Server..." -ForegroundColor Green
Set-Location $PSScriptRoot
& ".\.venv\Scripts\Activate.ps1"
python main.py
