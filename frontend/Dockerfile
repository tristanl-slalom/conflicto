# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production --prefer-offline --no-audit

# Copy OpenAPI spec (required for API generation)
COPY openapi.json ./openapi.json

# Copy source code
COPY frontend/ .

# Install all dependencies (including dev dependencies for build)
RUN npm install

# Build arguments for environment configuration
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_APP_TITLE=Conflicto

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build output to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
