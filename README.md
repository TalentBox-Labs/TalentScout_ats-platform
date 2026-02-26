# 🎯 TalentScout ATS Platform

**An AI-First Applicant Tracking System** built with modern technologies and intelligent automation.

## ⚡ Quick Links

- 📖 **[Installation Guide](INSTALLATION_GUIDE.md)** - Setup instructions
- 🚀 **[Getting Started](GETTING_STARTED.md)** - Quick start guide
- ✅ **[Setup Complete](SETUP_COMPLETE.md)** - What's been configured
- 🏗️ **[Project Structure](PROJECT_STRUCTURE.md)** - Directory layout
- 🔧 **[Quick Reference](QUICK_REFERENCE.md)** - Common commands

## 🌟 Key Features

### AI-Powered Capabilities
- 🤖 **Intelligent Resume Parsing** - Extract structured data from resumes automatically
- 🎯 **Smart Candidate Matching** - Vector-based semantic matching using embeddings
- 📝 **Auto-Generated Job Descriptions** - Create compelling JDs with AI
- ✉️ **Personalized Email Generation** - Context-aware communication
- 🔍 **Automated Screening** - AI evaluates candidates against requirements
- 💡 **Interview Question Generator** - Role-specific questions

### Core ATS Features
- 👥 **Multi-Tenant** - Support multiple organizations
- 📋 **Job Management** - Create, edit, track job postings
- 🏢 **Candidate Database** - Centralized talent pool
- 🎨 **Kanban Pipeline** - Visual application tracking
- 📅 **Interview Scheduling** - Coordinate interviews
- 📊 **Analytics Dashboard** - Hiring metrics and insights
- 🔐 **Role-Based Access** - Granular permissions

## 🛠️ Tech Stack

### Frontend
- **Next.js 14+** (App Router)
- **TypeScript**
- **Tailwind CSS** + Shadcn/ui
- **Zustand** + React Query

### Backend
- **FastAPI** (Python)
- **SQLAlchemy 2.0** (Async)
- **PostgreSQL 15** + pgvector
- **Redis** + Celery
- **OpenAI API** + LangChain
- **JWT Authentication**

### AI/ML
- **OpenAI GPT-4** - Reasoning and generation
- **Sentence Transformers** - Embeddings
- **spaCy** - NLP and entity extraction
- **pgvector** - Vector similarity search

## 🚀 Quick Start

### Option 1: Automated Start (PowerShell)

```powershell
# Start backend (includes Docker setup)
.\start-backend.ps1
```

### Option 2: Manual Start

```powershell
# 1. Start PostgreSQL and Redis
docker compose up -d postgres redis

# 2. Set up backend
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 3. Set up frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

## 📋 Prerequisites

### Required
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- Git ✅

### Optional
- Docker Desktop (recommended)
- Redis (or Docker)

**📖 See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed setup**

## 🎯 Current Status

### ✅ Completed (Ready to Use)
- ✅ **Authentication System** - Registration, login, JWT tokens
- ✅ **Database Models** - All tables and relationships
- ✅ **API Endpoints** - All CRUD operations defined
- ✅ **AI Service Layer** - Framework for AI features
- ✅ **Multi-Tenant** - Organization support
- ✅ **Docker Setup** - Development environment
- ✅ **Documentation** - Complete guides

### 🔄 Ready to Implement
- Frontend UI components
- AI resume parsing integration
- Candidate matching algorithm
- Email notification system
- File upload handling
- Interview scheduling UI

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Complete installation instructions |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Quick start guide with testing |
| [SETUP_COMPLETE.md](SETUP_COMPLETE.md) | What's been configured |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Directory structure explained |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture |

## 🧪 Test the API

Once the backend is running, visit: http://localhost:8000/docs

Try:
1. **Register** - POST `/api/v1/auth/register`
2. **Login** - POST `/api/v1/auth/login`
3. **Get User** - GET `/api/v1/auth/me` (with token)

## 🔑 Environment Variables

Create `backend/.env` from `.env.example`:

```env
# Required
DATABASE_URL=postgresql+asyncpg://ats_user:ats_password@localhost:5432/ats_platform
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key

# Optional
REDIS_URL=redis://localhost:6379/0
```

## 📊 Database Schema

Comprehensive schema with:
- Users & Organizations (multi-tenant)
- Jobs & Applications
- Candidates with vector embeddings
- Interviews & Assessments
- Communications & Integrations

See [database/schema.sql](database/schema.sql) for details.

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

## 📄 License

MIT License

## 🔗 Repository

**GitHub:** https://github.com/cyril-s-thomas/TalentScout_ats-platform

---

**Built with ❤️ using Next.js, FastAPI, and AI**
