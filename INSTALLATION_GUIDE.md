# 🛠️ Installation Guide - TalentScout ATS Platform

## Prerequisites

Before starting, ensure you have:

### Required:
- ✅ **Python 3.10+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- ✅ **Git** - Already have it ✅

### Optional (but recommended):
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/) (Easiest setup)
- **Redis** - [Download](https://redis.io/download) or use Docker

---

## 🚀 Setup Options

Choose the option that works best for you:

## Option A: With Docker (Recommended - Easiest)

### 1. Install Docker Desktop

Download and install: https://www.docker.com/products/docker-desktop/

After installation, make sure Docker Desktop is running.

### 2. Start Services with Docker

```powershell
# From project root
docker compose up -d postgres redis

# Wait for services to be healthy (30 seconds)
```

### 3. Set Up Python Backend

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

✅ **Backend running:** http://localhost:8000

---

## Option B: Without Docker (Manual PostgreSQL/Redis)

### 1. Install PostgreSQL

**Download:** https://www.postgresql.org/download/windows/

During installation:
- Set password for `postgres` user
- Default port: 5432
- Remember these credentials!

### 2. Enable pgvector Extension

```sql
-- Open pgAdmin or psql
-- Connect as postgres user

-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 3. Create Database

**Option A: Using pgAdmin**
1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `ats_platform`
4. Owner: `postgres`
5. Click Save

**Option B: Using psql**
```bash
# Open Command Prompt or PowerShell
psql -U postgres -c "CREATE DATABASE ats_platform;"
psql -U postgres -d ats_platform -c "CREATE EXTENSION vector;"
psql -U postgres -d ats_platform -c "CREATE EXTENSION \"uuid-ossp\";"
```

### 4. Update Database Connection

Edit `backend\.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ats_platform
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

### 5. Install Redis (Optional)

**Option A: Using Windows installer**
- Download: https://github.com/microsoftarchive/redis/releases
- Install and start service

**Option B: Skip Redis for now**
- Comment out Redis-related features in code
- Just focus on core API functionality

### 6. Set Up Backend

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

✅ **Backend running:** http://localhost:8000

---

## Option C: Cloud Database (No Local Install)

### Use Supabase (Free PostgreSQL)

1. **Create account:** https://supabase.com
2. **Create new project**
3. **Get connection string** from Settings → Database
4. **Update `.env`:**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
   ```

### Use Redis Cloud (Free Redis)

1. **Create account:** https://redis.com/try-free/
2. **Create database**
3. **Get connection string**
4. **Update `.env`:**
   ```env
   REDIS_URL=redis://:[password]@[host]:port
   ```

---

## 🧪 Verify Installation

### 1. Check PostgreSQL

```powershell
# Test connection
psql -U postgres -d ats_platform -c "SELECT version();"

# Should show PostgreSQL version
```

### 2. Check Backend API

Visit: http://localhost:8000/health

Should show:
```json
{
  "status": "healthy",
  "app": "TalentScout ATS Platform"
}
```

### 3. Check API Documentation

Visit: http://localhost:8000/docs

You should see interactive API documentation!

### 4. Test Authentication

In the API docs:
1. Register a new user
2. Login to get token
3. Use token to access protected endpoints

---

## 📱 Frontend Setup

Once backend is running:

```powershell
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend: http://localhost:3000

---

## 🔧 Configuration

### Minimum Required Environment Variables

Edit `backend\.env`:

```env
# Database - REQUIRED
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ats_platform

# Security - REQUIRED
SECRET_KEY=generate-a-random-secret-key-min-32-characters

# OpenAI - REQUIRED for AI features
OPENAI_API_KEY=sk-your-openai-api-key

# Redis - Optional (can skip for basic testing)
REDIS_URL=redis://localhost:6379/0
```

### Generate Secret Key

```python
# In Python
import secrets
print(secrets.token_urlsafe(32))
```

Copy the output to `SECRET_KEY` in `.env`

---

## 📊 Project Status

### ✅ Completed
- Project structure (Next.js + FastAPI)
- Database models and migrations
- Authentication system (JWT)
- All API routers created
- AI service layer framework
- Docker configuration
- Documentation

### 🔄 Ready to Implement
- Frontend UI components
- AI resume parsing (needs OpenAI key)
- Candidate matching algorithm
- Email notifications
- File upload handling
- Interview scheduling logic

### 🎯 Next Tasks
1. Install prerequisites (Python, PostgreSQL, Node.js)
2. Set up database (Option A, B, or C above)
3. Configure environment variables
4. Start backend API
5. Test authentication in Swagger docs
6. Set up frontend
7. Start building features!

---

## 📚 Resources

- **PostgreSQL Tutorial:** https://www.postgresql.org/docs/15/tutorial.html
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Next.js Docs:** https://nextjs.org/docs
- **Docker Docs:** https://docs.docker.com/get-started/

---

## 💡 Tips

1. **Start Simple:** Get backend running first, then add frontend
2. **Use Docker:** Much easier than manual PostgreSQL setup
3. **Check Logs:** `docker logs ats_postgres` or backend console output
4. **Test in Swagger:** Use http://localhost:8000/docs to test APIs
5. **One Step at a Time:** Don't try to run everything at once

---

## 🆘 Need Help?

If you run into issues:

1. **Check Prerequisites:** Make sure all required software is installed
2. **Check Ports:** Ensure ports 8000, 5432, 6379 are available
3. **Check Logs:** Look at terminal output for error messages
4. **Check .env:** Verify all required variables are set
5. **Database Connection:** Test PostgreSQL connection separately

---

**Ready to build?** Let's go! 🚀

Choose your installation option above and follow the steps.
