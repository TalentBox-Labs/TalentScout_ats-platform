# ATS Platform

A modern Applicant Tracking System (ATS) built with a full-stack architecture.

## Project Structure

```
ats-platform/
├── frontend/          # React + TypeScript frontend
├── backend/           # Node.js + Express backend
├── database/          # Database migrations and seeds
├── docs/              # Documentation
└── README.md
```

## Tech Stack

### Frontend
- React 18+ with TypeScript
- Vite for fast development
- Tailwind CSS for styling
- React Router for navigation
- Axios for API calls

### Backend
- Node.js + Express with TypeScript
- PostgreSQL database
- JWT authentication
- RESTful API architecture

### Database
- PostgreSQL
- Prisma ORM (or TypeORM)

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- PostgreSQL 14+
- Git

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ats-platform
```

2. Install dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd backend
npm install
```

3. Environment Setup

Create `.env` files in both frontend and backend directories (see `.env.example` files).

4. Database Setup
```bash
cd backend
npm run db:migrate
npm run db:seed
```

5. Run the application

**Backend (Terminal 1):**
```bash
cd backend
npm run dev
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:3000

## Features

- [ ] User authentication and authorization
- [ ] Job posting management
- [ ] Candidate profile management
- [ ] Application tracking
- [ ] Resume parsing
- [ ] Interview scheduling
- [ ] Email notifications
- [ ] Analytics dashboard

## Development

### Code Style
- ESLint + Prettier for code formatting
- Husky for pre-commit hooks

### Testing
```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT License
