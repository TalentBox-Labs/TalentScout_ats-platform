# Project Architecture

## Overview

The ATS Platform follows a modern **three-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         Frontend (React + TS)           │
│  - User Interface                       │
│  - State Management                     │
│  - API Communication                    │
└─────────────┬───────────────────────────┘
              │ HTTP/REST
              │
┌─────────────▼───────────────────────────┐
│       Backend (Node.js + Express)       │
│  - API Endpoints                        │
│  - Business Logic                       │
│  - Authentication & Authorization       │
│  - Data Validation                      │
└─────────────┬───────────────────────────┘
              │ SQL
              │
┌─────────────▼───────────────────────────┐
│         Database (PostgreSQL)           │
│  - Data Storage                         │
│  - Relationships                        │
│  - Constraints                          │
└─────────────────────────────────────────┘
```

## Frontend Architecture

### Technology Stack
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Zustand**: Lightweight state management (alternative to Redux)

### Folder Structure
```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components
│   ├── layouts/        # Layout components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API service functions
│   ├── store/          # State management
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
└── package.json
```

### Component Structure
```tsx
// Example component structure
components/
├── common/             # Generic reusable components
│   ├── Button/
│   ├── Input/
│   ├── Modal/
│   └── Card/
├── jobs/              # Job-related components
│   ├── JobCard/
│   ├── JobList/
│   └── JobForm/
└── candidates/        # Candidate components
    ├── CandidateCard/
    ├── CandidateList/
    └── CandidateProfile/
```

## Backend Architecture

### Technology Stack
- **Node.js**: Runtime environment
- **Express**: Web framework
- **TypeScript**: Type safety
- **PostgreSQL**: Relational database
- **JWT**: Authentication
- **Helmet**: Security middleware
- **Morgan**: Logging

### Folder Structure
```
backend/
├── src/
│   ├── config/         # Configuration files
│   │   └── database.ts
│   ├── controllers/    # Request handlers
│   │   └── *.controller.ts
│   ├── models/         # Data models & types
│   │   └── *.model.ts
│   ├── routes/         # API routes
│   │   └── *.routes.ts
│   ├── middleware/     # Custom middleware
│   │   ├── auth.middleware.ts
│   │   └── validation.middleware.ts
│   ├── services/       # Business logic
│   │   └── *.service.ts
│   ├── utils/          # Helper functions
│   │   └── *.util.ts
│   └── index.ts        # Entry point
├── tests/             # Test files
└── package.json
```

### Request Flow
```
Client Request
    ↓
Express Router
    ↓
Middleware (auth, validation)
    ↓
Controller (request handler)
    ↓
Service (business logic)
    ↓
Model (database operations)
    ↓
Database (PostgreSQL)
    ↓
Response back up the chain
```

## Database Architecture

### Schema Design

**Core Tables:**
- `users` - User accounts (employers and candidates)
- `jobs` - Job postings
- `applications` - Job applications
- `candidates` - Extended candidate profiles

**Relationships:**
- One-to-Many: User → Jobs (employer posts multiple jobs)
- Many-to-Many: Users ↔ Jobs (through Applications)
- One-to-One: User → Candidate Profile

### Data Flow
```sql
-- Example: Creating an application
1. Validate user is authenticated
2. Check job exists and is open
3. Check user hasn't already applied
4. Insert into applications table
5. Update job application count
6. Send notification to employer
```

## API Design

### RESTful Principles
- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Use proper status codes (200, 201, 400, 401, 404, 500)
- Version your API (e.g., /api/v1/...)
- Use consistent naming conventions

### Response Format
```json
{
  "status": "success" | "error",
  "data": { ... },
  "message": "Optional message",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

## Authentication Flow

```
1. User Registration
   POST /api/auth/register
   → Hash password
   → Store user in database
   → Return success message

2. User Login
   POST /api/auth/login
   → Validate credentials
   → Generate JWT token
   → Return token to client

3. Protected Routes
   GET /api/profile (with Authorization header)
   → Verify JWT token
   → Extract user info
   → Process request
   → Return data
```

## Security Considerations

### Backend Security
- **Helmet**: Security headers
- **CORS**: Cross-origin resource sharing
- **JWT**: Stateless authentication
- **Password Hashing**: bcrypt
- **Input Validation**: express-validator
- **SQL Injection Prevention**: Parameterized queries
- **Rate Limiting**: Prevent abuse

### Frontend Security
- **Environment Variables**: Sensitive data in .env
- **XSS Prevention**: React's built-in escaping
- **HTTPS Only**: In production
- **Token Storage**: localStorage or httpOnly cookies

## Deployment Architecture

```
┌─────────────────────┐
│   CDN (Frontend)    │
│   - Cloud Storage   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Cloud Load Balancing│
│ (HTTP(S) Load       │
│  Balancer)          │
│ - Reverse proxy     │
│ - Traffic           │
│   distribution      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   API Servers       │
│   - Cloud Run       │
│   - Multiple        │
│     instances       │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Database          │
│   - PostgreSQL      │
│   - Cloud SQL       │
└─────────────────────┘
```

**Cloud Load Balancing (HTTP(S) Load Balancer)**: Acts as a reverse proxy, distributing traffic to backend VMs or containers.

## Performance Optimization

### Backend
- Database connection pooling
- Query optimization and indexing
- Caching with Redis (future)
- Compression middleware

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Build optimization with Vite

## Scalability Considerations

### Horizontal Scaling
- Stateless backend (JWT authentication)
- Load balancer for multiple instances
- Database read replicas

### Vertical Scaling
- Optimize database queries
- Increase server resources
- CDN for static assets

## Testing Strategy

### Backend Testing
```typescript
// Unit tests (Jest)
- Individual functions
- Business logic
- Utility functions

// Integration tests
- API endpoints
- Database operations
- Middleware chains

// E2E tests
- Complete user flows
- Critical paths
```

### Frontend Testing
```typescript
// Unit tests (Vitest)
- Component rendering
- Utility functions
- Custom hooks

// Integration tests
- Component interactions
- Form submissions
- API calls

// E2E tests (Playwright/Cypress)
- User workflows
- Critical features
```

## Future Enhancements

### Potential Additions
1. **Redis Cache**: For session management and caching
2. **Message Queue**: For background jobs (Bull/Redis)
3. **File Storage**: S3 for resumes and documents
4. **Email Service**: SendGrid/AWS SES for notifications
5. **Real-time Features**: WebSockets for chat
6. **Analytics**: Track user behavior
7. **Search Engine**: Elasticsearch for advanced search
8. **Monitoring**: Sentry for error tracking

## Development Best Practices

1. **Code Style**: Use ESLint and Prettier
2. **Git Workflow**: Feature branches and PRs
3. **Commits**: Write descriptive commit messages
4. **Documentation**: Keep docs up to date
5. **Testing**: Write tests for critical features
6. **Reviews**: Code review before merging
7. **Security**: Regular dependency updates

## Resources

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [React Best Practices](https://react.dev/learn/thinking-in-react)
- [REST API Design](https://restfulapi.net/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)
