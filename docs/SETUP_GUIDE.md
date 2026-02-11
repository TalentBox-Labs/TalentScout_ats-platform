# ATS Platform - Setup Guide

This guide will help you set up the ATS Platform for development and production.

## Prerequisites

### Required Software
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** for version control
- **OpenAI API Key** for AI features

### Optional (for local development without Docker)
- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 15+ with pgvector extension
- **Redis** 7+

## Quick Start (Docker - Recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ats-platform
```

### 2. Configure Environment Variables

#### Backend Configuration
```bash
cd backend
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required: Secret Key (generate a secure random string)
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters

# Database (Docker defaults - no changes needed)
DATABASE_URL=postgresql+asyncpg://ats_user:ats_password@postgres:5432/ats_db

# Redis (Docker defaults - no changes needed)
REDIS_URL=redis://redis:6379/0

# Optional: Email provider
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@yourcompany.com

# Optional: AWS S3 for file storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
```

#### Frontend Configuration
```bash
cd ../frontend
cp .env.local.example .env.local
```

The defaults should work for Docker:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Start All Services
```bash
# From the project root
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)
- Celery worker

### 4. Run Database Migrations
```bash
# Create initial migration
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# Apply migration
docker-compose exec backend alembic upgrade head
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc

### 6. Create First User (via API)

Use the API documentation at http://localhost:8000/docs or use curl:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "organization_name": "My Company"
  }'
```

## Local Development Setup (Without Docker)

### Backend Setup

#### 1. Install Python Dependencies
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### 2. Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

#### 3. Set Up PostgreSQL

Install PostgreSQL 15+ and pgvector extension:
```bash
# Mac
brew install postgresql@15
brew install pgvector

# Ubuntu/Debian
sudo apt-get install postgresql-15 postgresql-contrib
sudo apt-get install postgresql-15-pgvector

# Windows: Download from postgresql.org
```

Create database:
```sql
CREATE DATABASE ats_db;
CREATE USER ats_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ats_db TO ats_user;

-- Connect to ats_db
\c ats_db

-- Enable pgvector extension
CREATE EXTENSION vector;
```

#### 4. Set Up Redis
```bash
# Mac
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows: Download from https://github.com/microsoftarchive/redis/releases
```

#### 5. Configure Environment
```bash
cp .env.example .env
```

Update `.env` with your local database:
```env
DATABASE_URL=postgresql+asyncpg://ats_user:your_password@localhost:5432/ats_db
REDIS_URL=redis://localhost:6379/0
# ... other settings
```

#### 6. Run Migrations
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

#### 7. Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 8. Start Celery Worker (Optional)
In a new terminal:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend Setup

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Configure Environment
```bash
cp .env.local.example .env.local
```

Update if needed:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

#### 3. Start Development Server
```bash
npm run dev
```

Access at http://localhost:3000

## Verify Installation

### Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "ATS Platform",
  "version": "1.0.0",
  "environment": "development"
}
```

### Check Database Connection
```bash
# Via Docker
docker-compose exec postgres psql -U ats_user -d ats_db -c "\dt"

# Local
psql -U ats_user -d ats_db -c "\dt"
```

### Check Redis
```bash
# Via Docker
docker-compose exec redis redis-cli ping

# Local
redis-cli ping
```

Should return: `PONG`

## Common Issues & Solutions

### Issue: Port Already in Use

**Solution**: Change ports in docker-compose.yml or stop conflicting services.

```bash
# Find process using port 8000 (Mac/Linux)
lsof -i :8000

# Find process using port 8000 (Windows)
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>
```

### Issue: Database Connection Failed

**Solution**: Verify PostgreSQL is running and credentials are correct.

```bash
# Check if PostgreSQL is running
docker-compose ps postgres
# or
sudo systemctl status postgresql

# Check logs
docker-compose logs postgres
```

### Issue: pgvector Extension Not Found

**Solution**: Install pgvector extension.

```bash
# Via Docker (already included in pgvector/pgvector image)
docker-compose exec postgres psql -U ats_user -d ats_db

# In psql
CREATE EXTENSION IF NOT EXISTS vector;
\dx  -- List extensions
```

### Issue: Module Import Errors (Python)

**Solution**: Ensure virtual environment is activated and dependencies are installed.

```bash
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Frontend Build Errors

**Solution**: Clear cache and reinstall dependencies.

```bash
cd frontend
rm -rf node_modules .next package-lock.json
npm install
npm run dev
```

### Issue: OpenAI API Errors

**Solution**: Verify API key is correct and has credits.

```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Development Workflow

### Making Database Changes

1. Modify models in `backend/app/models/`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. Review migration in `backend/alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```
5. To rollback:
   ```bash
   alembic downgrade -1
   ```

### Adding New API Endpoints

1. Create router in `backend/app/routers/`
2. Define schemas in `backend/app/schemas/`
3. Add business logic in `backend/app/services/`
4. Register router in `backend/app/main.py`
5. Test at http://localhost:8000/docs

### Adding Frontend Components

1. Create component in `frontend/components/`
2. Add types in `frontend/types/`
3. Use component in pages under `frontend/app/`

### Running Tests

Backend:
```bash
cd backend
pytest
pytest --cov=app tests/  # with coverage
```

Frontend:
```bash
cd frontend
npm test
npm run test:watch  # watch mode
```

## Production Deployment

See separate `DEPLOYMENT.md` guide for production setup instructions.

## Getting Help

- Check the [Implementation Status](IMPLEMENTATION_STATUS.md)
- Review the main [README.md](../README.md)
- Open an issue on GitHub
- Contact: support@atsplatform.com

## Next Steps

1. ✅ Complete setup
2. ✅ Verify all services are running
3. ⏭️ Read [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
4. ⏭️ Start implementing features
5. ⏭️ Refer to API documentation at `/docs`

---

**Happy coding! 🚀**
