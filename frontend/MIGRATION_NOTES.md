# Frontend Migration to Next.js

This frontend has been migrated from Vite to Next.js 14 with App Router.

## Changes Made

### Updated Configuration
- **tsconfig.json**: Updated for Next.js bundler mode with `jsx: "preserve"`
- **package.json**: Removed Vite scripts and react-router-dom, kept Next.js dependencies
- **.env.example**: Created with `NEXT_PUBLIC_API_URL` for API configuration

### Deprecated Files (can be removed)
- `vite.config.ts` - No longer needed with Next.js
- `src/main.tsx` - Replaced by Next.js app router
- `src/App.tsx` - Replaced by `app/page.tsx`
- `tsconfig.node.json` - Vite-specific configuration

### Active Structure
```
app/
  ├── (auth)/
  │   ├── login/page.tsx
  │   └── register/page.tsx
  ├── (dashboard)/
  │   ├── dashboard/page.tsx
  │   ├── jobs/page.tsx
  │   └── candidates/page.tsx
  ├── layout.tsx
  ├── page.tsx
  ├── globals.css
  └── providers.tsx
components/
  ├── dashboard/
  └── ui/
lib/
  └── api.ts (uses NEXT_PUBLIC_API_URL)
```

## Development

```bash
# Install dependencies
npm install

# Run development server on port 5173
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Copy `.env.example` to `.env.local` and configure:
- `NEXT_PUBLIC_API_URL`: FastAPI backend URL (default: http://localhost:8000)

## API Integration

The `lib/api.ts` client uses `NEXT_PUBLIC_API_URL` environment variable for backend communication. All API calls are prefixed with `/api/v1`.
