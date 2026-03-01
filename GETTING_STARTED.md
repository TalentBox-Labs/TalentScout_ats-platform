# 🚀 Getting Started - TalentScout ATS Platform

## Welcome!

Your AI-First Applicant Tracking System is ready to run. Follow these simple steps to get started.

## ⚡ Quick Start (Easiest Way)

### Option 1: One-Command Start (Windows PowerShell)

```powershell
# From project root
.\start-backend.ps1
```

This script will:
1. ✅ Start PostgreSQL and Redis (Docker)
2. ✅ Create Python virtual environment
3. ✅ Install dependencies
4. ✅ Run database migrations
5. ✅ Start FastAPI server

**Done!** Your API will be running at http://localhost:8000

### Option 2: Manual Setup (Step by Step)

If you prefer to run each step manually:

#### 1. Start Docker Services

```powershell
# Start PostgreSQL + Redis
docker-compose up -d postgres redis

# Verify they're running
docker ps
```

#### 2. Set Up Python Environment

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### 3. Initialize Database

```powershell
# Run migrations (creates all tables)
alembic upgrade head
```

#### 4. Start the API Server

```powershell
# Start with hot reload
uvicorn app.main:app --reload --port 8000
```

**Done!** API running at http://localhost:8000

## 🧪 Test Your Setup

### 1. Check Health

Open your browser: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "app": "TalentScout ATS Platform",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Explore API Documentation

Open: http://localhost:8000/docs

This is the **interactive API documentation** where you can:
- ✅ See all available endpoints
- ✅ Test APIs directly in the browser
- ✅ View request/response schemas
- ✅ Try authentication flow

### 3. Register a Test User

In the API docs (http://localhost:8000/docs):

1. Find **POST /api/v1/auth/register**
2. Click "Try it out"
3. Fill in:
   ```json
   {
     "email": "test@example.com",
     "password": "Test1234!",
     "first_name": "Test",
     "last_name": "User"
   }
   ```
4. Click "Execute"

You'll get back:
- ✅ Access token
- ✅ User profile
- ✅ Organization details

### 4. Test Login

1. Find **POST /api/v1/auth/login**
2. Click "Try it out"
3. Fill in form:
   - username: `test@example.com`
   - password: `Test1234!`
4. Click "Execute"

Copy the `access_token` from the response.

### 5. Test Protected Endpoint

1. Click the **Authorize** button (🔓 icon at top right)
2. Paste your access token
3. Click "Authorize"
4. Find **GET /api/v1/auth/me**
5. Click "Try it out" → "Execute"

You'll see your user profile! 🎉

## 📱 Frontend Setup (Next Step)

Once the backend is running, set up the frontend:

```powershell
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env.local

# Edit .env.local - add this line:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will run on: http://localhost:3000

## 🛠️ Development Workflow

### Daily Workflow

```powershell
# 1. Start services (if not running)
.\start-services.ps1

# 2. Start backend
cd backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# 3. Start frontend (new terminal)
cd frontend
npm run dev
```

### Working with Database

```powershell
# Create new migration after model changes
cd backend
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Access Database Directly

```powershell
# Connect to PostgreSQL
docker exec -it ats_postgres psql -U ats_user -d ats_platform

# Example queries
\dt                    # List tables
\d users              # Describe users table
SELECT * FROM users;  # Query users
\q                    # Quit
```

## 📚 What's Available

### Backend API Endpoints

All endpoints are at `http://localhost:8000/api/v1`:

**Authentication** (`/auth`)
- ✅ POST `/register` - Create account
- ✅ POST `/login` - Get access token
- ✅ GET `/me` - Get current user
- ✅ POST `/logout` - Logout

**Jobs** (`/jobs`)
- ✅ POST `/` - Create job
- ✅ GET `/` - List jobs
- ✅ GET `/{job_id}` - Get job details
- ✅ PUT `/{job_id}` - Update job
- ✅ DELETE `/{job_id}` - Delete job
- ✅ POST `/{job_id}/generate-description` - AI generate description

**Candidates** (`/candidates`)
- ✅ POST `/` - Create candidate
- ✅ POST `/upload-resume` - Upload resume (AI parsing)
- ✅ GET `/` - List candidates
- ✅ GET `/{candidate_id}` - Get candidate
- ✅ PUT `/{candidate_id}` - Update candidate
- ✅ DELETE `/{candidate_id}` - Delete candidate
- ✅ POST `/{candidate_id}/generate-summary` - AI summary

**Applications** (`/applications`)
- ✅ POST `/` - Create application
- ✅ GET `/` - List applications (with filters)
- ✅ GET `/{application_id}` - Get application
- ✅ PATCH `/{application_id}/status` - Update status
- ✅ POST `/{application_id}/screen` - AI screening
- ✅ POST `/{application_id}/score` - Calculate score
- ✅ POST `/{application_id}/notes` - Add note

**Interviews** (`/interviews`)
- ✅ POST `/` - Schedule interview
- ✅ GET `/` - List interviews
- ✅ GET `/{interview_id}` - Get interview
- ✅ PUT `/{interview_id}` - Update interview
- ✅ POST `/{interview_id}/feedback` - Add feedback
- ✅ POST `/{interview_id}/generate-questions` - AI questions

**AI Services** (`/ai`)
- ✅ POST `/parse-resume` - Parse resume with AI
- ✅ POST `/match-candidates/{job_id}` - Match candidates
- ✅ POST `/screen-candidate/{application_id}` - Screen candidate
- ✅ POST `/generate-job-description` - Generate job description
- ✅ POST `/generate-email` - Generate personalized email
- ✅ POST `/generate-screening-questions/{job_id}` - Generate questions

## 📊 Database Tables Created

When you run `alembic upgrade head`, these tables are created:

- ✅ **users** - User accounts
- ✅ **organizations** - Companies/tenants
- ✅ **organization_members** - User-org relationships
- ✅ **jobs** - Job postings
- ✅ **candidates** - Candidate profiles
- ✅ **candidate_experiences** - Work history
- ✅ **candidate_education** - Education history
- ✅ **candidate_skills** - Skills
- ✅ **applications** - Job applications
- ✅ **interviews** - Interview scheduling
- ✅ **assessments** - Technical assessments
- ✅ **communications** - Email/message log
- ✅ **integrations** - Third-party integrations

## 🎯 Key Features Ready

### Authentication ✅
- User registration with email
- JWT-based login
- Access token management
- Multi-tenant organization support
- Role-based access control

### Database ✅
- PostgreSQL 15 with pgvector extension
- Async SQLAlchemy for performance
- Alembic migrations
- Proper indexes and relationships

### AI Infrastructure ✅
- Vector embeddings support (pgvector)
- OpenAI integration ready
- Resume parser service
- Candidate matching service
- Email generation service

### API Documentation ✅
- Interactive Swagger UI
- ReDoc documentation
- Request/response examples
- Try APIs in browser

## 🐛 Common Issues

### "Docker is not running"
```powershell
# Start Docker Desktop
# Wait for it to fully start, then run:
docker-compose up -d postgres redis
```

### "Port 8000 is already in use"
```powershell
# Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### "Module not found"
```powershell
cd backend
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Cannot connect to database"
```powershell
# Check if PostgreSQL is running
docker ps | findstr postgres

# Check logs
docker logs ats_postgres

# Restart PostgreSQL
docker-compose restart postgres
```

## 📖 Next Steps

Now that your backend is running:

### 1. Test Authentication Flow
- Register a user in Swagger docs
- Login and get access token
- Test protected endpoints

### 2. Create First Job Posting
- Use POST /api/v1/jobs endpoint
- Add job title, description, requirements
- Test AI job description generation

### 3. Add Candidates
- Upload a resume (PDF/DOCX)
- Watch AI parse it automatically
- View extracted data

### 4. Set Up Frontend
- Follow frontend setup in README.md
- Connect to backend API
- Start building UI

### 5. Configure AI Features
- Add OpenAI API key to .env
- Test resume parsing
- Try candidate matching

## 🎊 You're All Set!

Your backend is **fully operational** with:
- ✅ Complete authentication system
- ✅ Database with all models
- ✅ AI service layer ready
- ✅ All API endpoints created
- ✅ Interactive documentation
- ✅ Docker development environment

**GitHub Repo:** https://github.com/cyril-s-thomas/TalentScout_ats-platform

## 📞 Get Help

- **API Docs:** http://localhost:8000/docs
- **Check logs:** `docker-compose logs -f backend`
- **Database:** `docker exec -it ats_postgres psql -U ats_user -d ats_platform`
- **Redis:** `docker exec -it ats_redis redis-cli`

---

Happy coding! 🎉 Start building the AI-powered ATS of the future! 🚀
