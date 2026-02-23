# Multi-stage build for production
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy application files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Copy the standalone build output
COPY --from=builder /app/.next/standalone ./

# Copy the static files
COPY --from=builder /app/.next/static ./.next/static

# Copy public folder if it exists
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Set environment variables
ENV PORT=3000
ENV NODE_ENV=production

# Start the server
CMD ["node", "server.js"]