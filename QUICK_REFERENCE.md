# Quick Reference Guide - ATS Platform

Essential commands and information for daily development.

## 🚀 Quick Start

```bash
# Start everything with Docker
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend
```

## 📁 Project Locations

```
Backend:   h:\Crypto FInTech\ats-platform\backend
Frontend:  h:\Crypto FInTech\ats-platform\frontend
Docs:      h:\Crypto FInTech\ats-platform\docs
```

## 🔧 Development Commands

### Backend (FastAPI)

```bash
# Start backend (local)
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload

# Run tests
pytest
pytest --cov=app tests/

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Frontend (Next.js)

```bash
# Start frontend (local)
cd frontend
npm run dev

# Build for production
npm run build
npm start

# Run tests
npm test

# Install new package
npm install package-name

# Type checking
npm run type-check

# Linting
npm run lint
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Stop and remove containers
docker-compose down

# Remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart service
docker-compose restart backend
```

## 🗄️ Database Commands

### Via Docker

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U ats_user -d ats_db

# Backup database
docker-compose exec postgres pg_dump -U ats_user ats_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U ats_user -d ats_db < backup.sql

# List tables
docker-compose exec postgres psql -U ats_user -d ats_db -c "\dt"

# Check pgvector extension
docker-compose exec postgres psql -U ats_user -d ats_db -c "\dx"
```

### Local

```bash
# Access database
psql -U ats_user -d ats_db

# Common psql commands
\l          # List databases
\dt         # List tables
\d+ table   # Describe table
\q          # Quit
```

### Redis Commands

```bash
# Access Redis
docker-compose exec redis redis-cli

# Common commands
PING        # Test connection
KEYS *      # List all keys
FLUSHALL    # Clear all data (CAUTION)
INFO        # Server info
```

## 🔑 Environment Variables

### Backend (.env)

```bash
# Required
OPENAI_API_KEY=sk-...
SECRET_KEY=...
DATABASE_URL=...

# Optional
SENDGRID_API_KEY=...
AWS_ACCESS_KEY_ID=...
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 🌐 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Docs (Alt) | http://localhost:8000/redoc | ReDoc |
| Health Check | http://localhost:8000/health | Status endpoint |

## 📊 Useful SQL Queries

```sql
-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM jobs;
SELECT COUNT(*) FROM candidates;

-- Recent applications
SELECT * FROM applications ORDER BY created_at DESC LIMIT 10;

-- Jobs with applications count
SELECT j.title, COUNT(a.id) as app_count 
FROM jobs j 
LEFT JOIN applications a ON j.id = a.job_id 
GROUP BY j.id, j.title;
```

## 🐛 Debugging

### Check Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Common Issues

#### Port in use
```bash
# Find process
lsof -i :8000     # Mac/Linux
netstat -ano | findstr :8000    # Windows

# Kill process
kill -9 <PID>
```

#### Database connection failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### Frontend won't start
```bash
# Clear cache
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
pytest tests/test_models.py -v
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:watch
npm run test:coverage
```

## 📦 Adding New Features

### New Database Model

1. Create model in `backend/app/models/`
2. Add to `__init__.py`
3. Create migration: `alembic revision --autogenerate -m "Add model"`
4. Review and apply: `alembic upgrade head`

### New API Endpoint

1. Create router in `backend/app/routers/`
2. Define schemas in `backend/app/schemas/`
3. Add service logic in `backend/app/services/`
4. Register in `backend/app/main.py`

### New Frontend Page

1. Create page in `frontend/app/(dashboard)/`
2. Add types in `frontend/types/`
3. Create components in `frontend/components/`
4. Add API calls in `frontend/lib/api.ts`

## 🔐 Security Checklist

- [ ] SECRET_KEY is secure (32+ characters)
- [ ] OPENAI_API_KEY is not committed
- [ ] .env files are in .gitignore
- [ ] Database credentials are strong
- [ ] CORS origins are configured correctly
- [ ] JWT expiration is set appropriately

## 📚 Documentation

- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Setup instructions
- [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) - Progress
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - What's built

## 💡 Tips

1. **Always activate venv** before running Python commands
2. **Check logs first** when debugging
3. **Use Docker** for consistent environment
4. **Run migrations** after model changes
5. **Clear cache** if frontend behaves oddly
6. **Test locally** before committing
7. **Update docs** when adding features

## 🆘 Getting Help

1. Check documentation in `/docs`
2. Review API docs at `/docs`
3. Check logs: `docker-compose logs -f`
4. Search codebase for examples
5. Open GitHub issue

---

**Keep this handy for daily development!**
