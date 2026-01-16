FROM node:20-slim

# Install necessary system dependencies for Claude SDK
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for subprocess stability
ENV NODE_ENV=production \
    TMPDIR=/tmp \
    HOME=/home/node

# Ensure proper permissions on temp directory
RUN mkdir -p /tmp && chmod 1777 /tmp

WORKDIR /app

# Copy backend package files
COPY server/package*.json ./server/
WORKDIR /app/server
RUN npm install

# Copy backend code
COPY server/ ./

# Copy frontend files
COPY renderer/ /app/renderer/

# Change ownership to non-root user (node:node exists in base image)
RUN chown -R node:node /app

# Switch to non-root user
USER node

WORKDIR /app/server

EXPOSE 3001

CMD ["npm", "start"]
