# 🚀 AUTO NOTIFY WEB APP - COMPLETE SETUP SCRIPT
# Run dit script om de hele web applicatie op te zetten

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   AUTO NOTIFY WEB APP - SETUP" -ForegroundColor Cyan  
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Check if we're in the right directory
$currentPath = Get-Location
Write-Host "Current directory: $currentPath" -ForegroundColor Gray

# Navigate to web-app
if (-not (Test-Path "web-app")) {
    Write-Host "✓ Creating web-app directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "web-app" | Out-Null
}

Set-Location "web-app"

# ==============================================
# FRONTEND SETUP
# ==============================================

Write-Host ""
Write-Host "[1/5] Setting up Next.js Frontend..." -ForegroundColor Yellow

if (-not (Test-Path "frontend")) {
    New-Item -ItemType Directory -Path "frontend" | Out-Null
}

Set-Location "frontend"

# Check Node.js
Write-Host "  Checking Node.js..." -ForegroundColor Gray
try {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Node.js not found! Please install Node.js first." -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
if (Test-Path "package.json") {
    Write-Host "  Installing npm packages..." -ForegroundColor Gray
    npm install
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  package.json not found - creating..." -ForegroundColor Yellow
    
    # Initialize Next.js project
    npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
    
    # Install additional packages
    npm install @tanstack/react-query axios zustand
    npm install @headlessui/react @heroicons/react
    npm install react-hook-form zod @hookform/resolvers
    npm install clsx date-fns recharts sonner
    
    Write-Host "  ✓ Frontend initialized" -ForegroundColor Green
}

Set-Location ..

# ==============================================
# BACKEND SETUP  
# ==============================================

Write-Host ""
Write-Host "[2/5] Setting up Python FastAPI Backend..." -ForegroundColor Yellow

if (-not (Test-Path "api")) {
    New-Item -ItemType Directory -Path "api" | Out-Null
}

Set-Location "api"

# Check Python
Write-Host "  Checking Python..." -ForegroundColor Gray
try {
    $pythonVersion = python --version
    Write-Host "  ✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found!" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
.\.venv\Scripts\Activate.ps1

# Install Python packages
if (Test-Path "requirements.txt") {
    Write-Host "  Installing Python packages..." -ForegroundColor Gray
    pip install -q -r requirements.txt
    Write-Host "  ✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  requirements.txt not found" -ForegroundColor Yellow
}

Set-Location ..

# ==============================================
# COPY SCRAPERS FROM ORIGINAL BOT
# ==============================================

Write-Host ""
Write-Host "[3/5] Copying scrapers from original bot..." -ForegroundColor Yellow

$originalBotPath = ".."

if (Test-Path "$originalBotPath\scrapers") {
    Write-Host "  Copying scrapers..." -ForegroundColor Gray
    Copy-Item -Path "$originalBotPath\scrapers" -Destination "api\" -Recurse -Force
    Write-Host "  ✓ Scrapers copied" -ForegroundColor Green
}

if (Test-Path "$originalBotPath\utils") {
    Write-Host "  Copying utils..." -ForegroundColor Gray
    Copy-Item -Path "$originalBotPath\utils" -Destination "api\" -Recurse -Force
    Write-Host "  ✓ Utils copied" -ForegroundColor Green
}

if (Test-Path "$originalBotPath\database") {
    Write-Host "  Copying database..." -ForegroundColor Gray
    Copy-Item -Path "$originalBotPath\database" -Destination "api\" -Recurse -Force
    Write-Host "  ✓ Database copied" -ForegroundColor Green
}

if (Test-Path "$originalBotPath\notifiers") {
    Write-Host "  Copying notifiers..." -ForegroundColor Gray
    Copy-Item -Path "$originalBotPath\notifiers" -Destination "api\" -Recurse -Force
    Write-Host "  ✓ Notifiers copied" -ForegroundColor Green
}

# ==============================================
# ENVIRONMENT SETUP
# ==============================================

Write-Host ""
Write-Host "[4/5] Setting up environment..." -ForegroundColor Yellow

# Copy .env if exists
if (Test-Path "$originalBotPath\.env") {
    Write-Host "  Copying .env file..." -ForegroundColor Gray
    Copy-Item -Path "$originalBotPath\.env" -Destination "api\.env" -Force
    Write-Host "  ✓ Environment variables copied" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  No .env file found in original bot" -ForegroundColor Yellow
}

# ==============================================
# CREATE STARTUP SCRIPTS
# ==============================================

Write-Host ""
Write-Host "[5/5] Creating startup scripts..." -ForegroundColor Yellow

# Dev script
$devScript = @"
# Development startup script
Write-Host "Starting Auto Notify Web App..." -ForegroundColor Cyan
Write-Host ""

# Start backend in background
Write-Host "[1/2] Starting FastAPI backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd api; .\.venv\Scripts\Activate.ps1; uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 2

# Start frontend
Write-Host "[2/2] Starting Next.js frontend..." -ForegroundColor Yellow  
Set-Location frontend
npm run dev
"@

Set-Content -Path "dev.ps1" -Value $devScript
Write-Host "  ✓ dev.ps1 created" -ForegroundColor Green

# ==============================================
# DONE
# ==============================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   ✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review files in web-app/frontend/app/" -ForegroundColor White
Write-Host "2. Start development:" -ForegroundColor White
Write-Host "   .\dev.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Access the app:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. To deploy to Vercel:" -ForegroundColor White
Write-Host "   - Push to GitHub" -ForegroundColor Gray
Write-Host "   - Import in Vercel dashboard" -ForegroundColor Gray
Write-Host "   - Add environment variables" -ForegroundColor Gray
Write-Host "   - Deploy!" -ForegroundColor Gray
Write-Host ""
