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
FROM nginx:alpine AS runner

# Copy the build output to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Start nginx with dynamic port
CMD ["sh", "-c", "sed -i 's/80/'$PORT'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]