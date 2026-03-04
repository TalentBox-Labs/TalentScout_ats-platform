# Quick Start Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **PostgreSQL** (v14 or higher) - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/)
- A code editor (VS Code recommended)

## Setup Instructions

### 1. Database Setup

**Create a new PostgreSQL database:**

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ats_platform;

# Exit psql
\q
```

**Run the schema:**

```bash
psql -U postgres -d ats_platform -f database/schema.sql
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your database credentials
# Use your preferred text editor
```

**Update the `.env` file with your settings:**

```env
NODE_ENV=development
PORT=3000

DB_HOST=localhost
DB_PORT=5432
DB_NAME=ats_platform
DB_USER=postgres
DB_PASSWORD=your_postgres_password

JWT_SECRET=your-secret-key-here
JWT_EXPIRES_IN=7d

CORS_ORIGIN=http://localhost:5173
```

**Start the backend server:**

```bash
npm run dev
```

The backend should now be running on `http://localhost:3000`

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start the development server
npm run dev
```

The frontend should now be running on `http://localhost:5173`

### 4. Verify Setup

1. Open your browser and go to `http://localhost:5173`
2. You should see the ATS Platform welcome page
3. Check that the backend status shows as "✅ ATS Platform API is running"

## Testing the API

You can test the API endpoints using curl, Postman, or any API client:

```bash
# Health check
curl http://localhost:3000/health

# API info
curl http://localhost:3000/api
```

## Common Issues

### Port Already in Use

If you get a "port already in use" error:

**For backend (port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

**For frontend (port 5173):**
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5173 | xargs kill -9
```

### Database Connection Error

- Verify PostgreSQL is running
- Check your database credentials in `.env`
- Ensure the database exists: `psql -U postgres -l`

### Module Not Found

```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

Once everything is running:

1. **Explore the codebase** - Familiarize yourself with the project structure
2. **Read the API documentation** - Check `docs/API.md` (coming soon)
3. **Start building features** - Use the example controllers and models as templates
4. **Set up authentication** - Implement user registration and login
5. **Create your first endpoint** - Try creating a simple CRUD operation

## Development Workflow

```bash
# Backend development
cd backend
npm run dev          # Start dev server with hot reload
npm run build        # Build for production
npm test             # Run tests

# Frontend development
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm test             # Run tests
```

## Useful Commands

```bash
# Database
psql -U postgres -d ats_platform              # Access database
psql -U postgres -d ats_platform -f file.sql  # Run SQL file

# Git
git init                                       # Initialize git repo
git add .                                      # Stage all changes
git commit -m "Initial commit"                 # Commit changes

# Package management
npm install <package>                          # Install new package
npm uninstall <package>                        # Remove package
npm update                                     # Update all packages
```

## Resources

- [React Documentation](https://react.dev/)
- [Express Documentation](https://expressjs.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev/)

## Need Help?

- Check the main README.md for more details
- Review the code comments and examples
- Search for solutions on Stack Overflow
- Create an issue in the repository

Happy coding! 🚀
