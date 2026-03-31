# PowerShell run script - activates venv and runs bot

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "❌ Virtual environment niet gevonden!" -ForegroundColor Red
    Write-Host "Run eerst: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Run bot
Write-Host "🚀 Starting Notification Bot..." -ForegroundColor Cyan
Write-Host ""

python main.py $args
