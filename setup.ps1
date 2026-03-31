# PowerShell setup script voor Windows

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Multi-Platform Notification Bot - Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python niet gevonden! Installeer Python 3.8+ eerst." -ForegroundColor Red
    Write-Host "Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ $pythonVersion gevonden" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "✓ Virtual environment bestaat al" -ForegroundColor Green
} else {
    python -m venv .venv
    Write-Host "✓ Virtual environment aangemaakt" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment geactiveerd" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
Write-Host "Dit kan enkele minuten duren..." -ForegroundColor Gray
python -m pip install --upgrade pip | Out-Null
pip install -r requirements.txt
Write-Host "✓ Dependencies geïnstalleerd" -ForegroundColor Green

# Install Playwright browsers
Write-Host ""
Write-Host "[5/5] Installing Playwright browsers (voor Facebook)..." -ForegroundColor Yellow
Write-Host "Dit kan enkele minuten duren..." -ForegroundColor Gray
playwright install chromium
Write-Host "✓ Playwright browsers geïnstalleerd" -ForegroundColor Green

# Create directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$dirs = @("data", "logs", "cookies")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✓ Created $dir/" -ForegroundColor Green
    }
}

# Copy .env.example to .env if not exists
Write-Host ""
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file aangemaakt - VUL JE CREDENTIALS IN!" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file bestaat al" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  ✅ Setup Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Volgende stappen:" -ForegroundColor Yellow
Write-Host "1. Edit config.yaml met je zoek criteria" -ForegroundColor White
Write-Host "2. Edit .env met je notificatie credentials" -ForegroundColor White
Write-Host "3. Test de bot:" -ForegroundColor White
Write-Host "   python main.py --test" -ForegroundColor Cyan
Write-Host "4. Run de bot:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Voor meer info: zie README.md" -ForegroundColor Gray
Write-Host ""
