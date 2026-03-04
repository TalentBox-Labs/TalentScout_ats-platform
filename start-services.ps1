# Start only Docker services (PostgreSQL + Redis)
# Run backend manually afterward

Write-Host "🚀 Starting TalentScout ATS Platform Services..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if (-not $dockerAvailable) {
    Write-Host "❌ Docker is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please either:" -ForegroundColor Yellow
    Write-Host "  1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    Write-Host "  2. Install PostgreSQL manually: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📖 See INSTALLATION_GUIDE.md for detailed instructions" -ForegroundColor Green
    exit 1
}

docker compose up -d postgres redis

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 PostgreSQL running on: localhost:5432" -ForegroundColor Green
    Write-Host "🔴 Redis running on: localhost:6379" -ForegroundColor Green
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  docker compose logs -f postgres" -ForegroundColor Gray
    Write-Host "  docker compose logs -f redis" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To stop services:" -ForegroundColor Yellow
    Write-Host "  docker compose down" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "❌ Failed to start services. Make sure Docker Desktop is running!" -ForegroundColor Red
    Write-Host "   You may need to start Docker Desktop first." -ForegroundColor Yellow
    exit 1
}
