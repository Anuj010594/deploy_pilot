# Frontend Setup Guide

## Prerequisites Installation

Since Node.js is not currently installed on your system, you'll need to install it first.

### Option 1: Install Node.js via apt (Recommended for Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Node.js and npm
sudo apt install -y nodejs npm

# Verify installation
node --version
npm --version
```

### Option 2: Install Node.js via nvm (Node Version Manager)

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell configuration
source ~/.bashrc

# Install Node.js LTS
nvm install --lts

# Verify installation
node --version
npm --version
```

### Option 3: Install Node.js via Official Repository

```bash
# Download and import Node.js repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Install Node.js
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

## Quick Start

Once Node.js is installed:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Production Deployment

### Build for Production

```bash
cd frontend
npm install
npm run build
```

The optimized build will be in the `dist/` directory.

### Serve Production Build

```bash
# Preview the production build
npm run preview

# Or use a static file server
npx serve -s dist -l 3000
```

### Docker Deployment (Recommended)

If you have Docker installed:

```bash
# Build Docker image
cd frontend
docker build -t project-detector-frontend .

# Run container
docker run -d -p 80:80 --name frontend project-detector-frontend

# Or use docker-compose for full stack
docker-compose up -d
```

## Testing the Application

1. Ensure backend is running on `http://localhost:8000`
2. Start frontend: `npm run dev`
3. Open browser to `http://localhost:3000`
4. Test with:
   - GitHub URL: Try any public repository
   - ZIP Upload: Upload a project ZIP file
   - Adjust confidence threshold and see results

## Troubleshooting

### Port Already in Use

```bash
# Change port in vite.config.js
# Or kill the process using the port
lsof -ti:3000 | xargs kill -9
```

### API Connection Issues

- Check backend is running: `curl http://localhost:8000/api/health`
- Verify CORS settings in backend
- Check browser console for errors

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Environment Configuration

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

For production, update API URL accordingly.
