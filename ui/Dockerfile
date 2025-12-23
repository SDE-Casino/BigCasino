# Use Node.js LTS version
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose port 3000 (Vite default port)
EXPOSE 3000

# Run development server
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]