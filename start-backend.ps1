# TalentScout ATS Platform - Backend Startup Script
# Run this script to start the backend API

Write-Host "🚀 Starting TalentScout ATS Platform Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
Write-Host "📦 Step 1: Checking Docker..." -ForegroundColor Yellow
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerAvailable) {
    Write-Host "✅ Docker found - Starting services..." -ForegroundColor Green
    docker compose up -d postgres redis
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start Docker services. Make sure Docker Desktop is running!" -ForegroundColor Red
        Write-Host "   Or skip Docker and use local PostgreSQL (see INSTALLATION_GUIDE.md)" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Docker services started (PostgreSQL + Redis)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker not found - You'll need to:" -ForegroundColor Yellow
    Write-Host "   1. Install Docker Desktop, OR" -ForegroundColor Gray
    Write-Host "   2. Install PostgreSQL manually" -ForegroundColor Gray
    Write-Host "   See INSTALLATION_GUIDE.md for detailed instructions" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Do you have PostgreSQL running locally? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

Write-Host "✅ Docker services started (PostgreSQL + Redis)" -ForegroundColor Green
Write-Host ""

# Wait for services to be healthy
Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if virtual environment exists
$venvPath = "backend\venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "📦 Step 2: Creating Python virtual environment..." -ForegroundColor Yellow
    Push-Location backend
    python -m venv venv
    Pop-Location
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment and install dependencies
Write-Host "📦 Step 3: Installing Python dependencies..." -ForegroundColor Yellow
Push-Location backend

& "$venvPath\Scripts\Activate.ps1"

$requirementsModified = (Get-Item requirements.txt).LastWriteTime
$installedMarker = ".installed"

if (-Not (Test-Path $installedMarker) -or (Get-Item requirements.txt).LastWriteTime -gt (Get-Item $installedMarker).LastWriteTime) {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        New-Item -Path $installedMarker -ItemType File -Force | Out-Null
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "✅ Dependencies already up to date" -ForegroundColor Green
}

Write-Host ""

# Run database migrations
Write-Host "📊 Step 4: Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database migrations applied" -ForegroundColor Green
} else {
    Write-Host "⚠️  Migration warning (may be expected on first run)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Starting FastAPI server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 API:      http://localhost:8000" -ForegroundColor Green
Write-Host "📚 Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "📖 ReDoc:    http://localhost:8000/redoc" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn app.main:app --reload --port 8000

Pop-Location
