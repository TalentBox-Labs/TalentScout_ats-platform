# 🎉 TalentScout ATS Platform - Complete Setup Guide

## ✅ Phase 2 Complete: Authentication & Database Setup

Your backend is now **fully configured** with authentication, database, and all infrastructure!

## 📦 What Was Set Up

### 1. **Environment Configuration** ✅
- ✅ Complete `.env` file with all required settings
- ✅ Database URL configured (PostgreSQL with async support)
- ✅ Redis for caching and Celery
- ✅ JWT secrets and token expiration
- ✅ CORS settings
- ✅ OpenAI API configuration (for AI features)

### 2. **Docker Infrastructure** ✅
- ✅ PostgreSQL 15 with pgvector extension (for AI embeddings)
- ✅ Redis for caching and task queue
- ✅ Celery worker for background tasks
- ✅ Proper health checks and networking
- ✅ Database initialization script

### 3. **Authentication System** ✅
- ✅ User registration with organization creation
- ✅ JWT-based login system
- ✅ Access and refresh tokens
- ✅ Password hashing (bcrypt)
- ✅ Get current user endpoint
- ✅ Multi-tenant support (organizations)
- ✅ Role-based access control

### 4. **Database Models** ✅
- ✅ User model with OAuth support
- ✅ Organization model (multi-tenant)
- ✅ OrganizationMember (user-org relationships)
- ✅ Role-based permissions
- ✅ All application models (Job, Candidate, Application, Interview, etc.)

## 🚀 Quick Start (3 Steps)

### Step 1: Start Docker Services

```bash
# From project root
docker-compose up -d postgres redis

# Verify services are running
docker ps
```

You should see:
- `ats_postgres` - Running on port 5432
- `ats_redis` - Running on port 6379

### Step 2: Install Backend Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Initialize Database & Run Server

```bash
# Still in backend directory

# Initialize database tables
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

Your backend API is now running! 🎯

**Access:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Test the Authentication

### 1. Register a New User

**POST** `http://localhost:8000/api/v1/auth/register`

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe"
  },
  "organization": {
    "id": "uuid",
    "name": "John's Organization"
  }
}
```

### 2. Login

**POST** `http://localhost:8000/api/v1/auth/login`

Form data:
- username: `user@example.com`
- password: `SecurePassword123!`

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Get Current User

**GET** `http://localhost:8000/api/v1/auth/me`

Headers:
- Authorization: `Bearer {your_access_token}`

Response:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": null,
  "title": null,
  "avatar_url": null,
  "bio": null,
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-02-12T00:00:00",
  "timezone": "UTC"
}
```

## 📚 API Documentation

Once the server is running, visit:

**Swagger UI:** http://localhost:8000/docs

Here you'll find:
- ✅ Authentication endpoints (`/auth/`)
- ✅ Job management (`/jobs/`)
- ✅ Candidate management (`/candidates/`)
- ✅ Application pipeline (`/applications/`)
- ✅ Interview scheduling (`/interviews/`)
- ✅ AI services (`/ai/`)

## 🔧 Configuration Details

### Environment Variables (`.env`)

#### Required Settings:
```env
DATABASE_URL=postgresql+asyncpg://ats_user:ats_password@localhost:5432/ats_platform
SECRET_KEY=your-super-secret-key-change-this-in-production
OPENAI_API_KEY=your-openai-api-key  # Required for AI features
```

#### Optional Settings:
- AWS S3 credentials (for file storage)
- SendGrid/Resend API key (for emails)
- OAuth client IDs (for social login)
- Job board API keys (for integrations)

### Database Schema

The database includes:
- **users** - User accounts with OAuth support
- **organizations** - Multi-tenant companies
- **organization_members** - User-organization relationships with roles
- **jobs** - Job postings
- **candidates** - Candidate profiles
- **applications** - Job applications
- **interviews** - Interview scheduling
- **assessments** - Technical assessments
- **communications** - Email/message tracking
- **integrations** - Third-party integrations

### Roles

User roles in the system:
- **ADMIN** - Full system access
- **HIRING_MANAGER** - Manage jobs and hiring process
- **RECRUITER** - Source candidates, manage applications
- **INTERVIEWER** - Conduct interviews, provide feedback
- **VIEWER** - Read-only access

## 🎯 Next Steps

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local

# Edit .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will run on: http://localhost:3000

### Implement Core Features

Now that auth and database are ready, you can implement:

1. **Job Management**
   - Create job postings
   - Edit/delete jobs
   - Job templates
   - AI-generate job descriptions

2. **Candidate Management**
   - Upload resumes
   - AI resume parsing
   - Candidate database
   - Search and filters

3. **Application Pipeline**
   - Kanban board
   - Stage management
   - AI screening
   - Bulk actions

4. **AI Features**
   - Resume parsing (GPT-4)
   - Candidate matching (embeddings)
   - Screening questions generation
   - Email personalization

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs ats_postgres

# Restart if needed
docker-compose restart postgres
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (Windows)
taskkill /PID <PID> /F

# Or change port in .env
PORT=8001
```

### Alembic Migration Error
```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head

# Or drop database and recreate
docker-compose down -v
docker-compose up -d postgres redis
alembic upgrade head
```

### Module Not Found Error
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

## 📖 Useful Commands

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Reset everything (removes data!)
docker-compose down -v
```

### Database
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Connect to database
docker exec -it ats_postgres psql -U ats_user -d ats_platform
```

### Backend
```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Check code style
black app/
flake8 app/
```

## 🎊 Summary

✅ **Backend API** - Running with FastAPI  
✅ **Database** - PostgreSQL with pgvector  
✅ **Authentication** - JWT-based auth system  
✅ **Multi-tenant** - Organization support  
✅ **API Docs** - Interactive Swagger UI  
✅ **Docker** - Development environment ready  
✅ **Redis** - Caching and task queue  
✅ **All Routers** - Endpoints for all features  

## 📞 Need Help?

- Check API docs: http://localhost:8000/docs
- Review code in `backend/app/routers/`
- Check logs: `docker-compose logs -f`
- Read the plan: `.cursor/plans/ai-first_ats_platform_7a269daa.plan.md`

---

**Your TalentScout ATS Platform backend is fully operational!** 🚀

Start implementing features or test the APIs in the Swagger docs!
