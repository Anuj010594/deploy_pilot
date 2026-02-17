# Project Detector - Frontend

> **Zero-Dependency Vanilla JavaScript Frontend for Project Detection API**

A lightweight, production-ready frontend application for detecting programming languages, frameworks, and build tools in repositories. Built with pure HTML, CSS, and JavaScript - no build tools required!

## 🌟 Features

- **🔍 Dual Input Methods**
  - Scan GitHub repositories via URL
  - Upload ZIP files directly (with drag & drop support)

- **🎯 Smart Detection**
  - Adjustable confidence threshold slider (0.0 - 1.0)
  - Real-time API health monitoring
  - Detailed detection results with confidence levels

- **⚡ Zero Dependencies**
  - No React, Vue, or any framework
  - No npm packages to install
  - No build process needed
  - Works with ANY Node.js version (or none at all!)

- **🎨 Modern UI**
  - Beautiful gradient design
  - Smooth animations
  - Fully responsive
  - Accessible and user-friendly

## 🚀 Quick Start

### Prerequisites

- Python 3.6+ (for serving the frontend)
- Backend API running on `http://localhost:8000`

### Installation & Running

```bash
# Navigate to frontend directory
cd frontend

# Start the server
python3 serve.py

# Or using npm (optional)
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## 📁 Project Structure

```
frontend/
├── public/              # Static files
│   ├── index.html      # Main HTML page
│   ├── styles.css      # All styles (CSS variables, animations)
│   └── app.js          # Application logic (vanilla JS)
├── serve.py            # Python HTTP server with API proxy
├── package.json        # Minimal config (no dependencies!)
├── README.md           # This file
└── DEPLOYMENT_INFO.txt # Deployment details
```

## 🔧 Configuration

### Backend URL

The frontend expects the backend API at `http://localhost:8000`. To change this:

**Edit `serve.py`:**
```python
BACKEND_URL = "http://your-backend-url:port"
```

### Port Configuration

**Edit `serve.py`:**
```python
PORT = 3000  # Change to your preferred port
```

## 📡 API Integration

The frontend communicates with these backend endpoints:

### Health Check
```
GET /api/health
```

### Scan Repository
```
POST /api/scan
Content-Type: multipart/form-data

Parameters:
- github_url (optional): GitHub repository URL
- zip_file (optional): ZIP file upload
- min_confidence (optional): Minimum confidence threshold (default: 0.45)
```

**Response Format:**
```json
{
  "detections": [
    {
      "primary_language": "Node.js",
      "framework": null,
      "build_tool": "yarn",
      "build_required": true,
      "build_command": "yarn build",
      "install_command": null,
      "confidence_score": 0.65,
      "confidence_level": "moderate",
      "detected_files": ["package.json", "yarn.lock"]
    }
  ],
  "primary": {
    "primary_language": "Node.js",
    "framework": null,
    "build_tool": "yarn",
    "build_required": true,
    "build_command": "yarn build",
    "install_command": null,
    "confidence_score": 0.65,
    "confidence_level": "moderate",
    "detected_files": ["package.json", "yarn.lock"]
  },
  "min_confidence_threshold": 0.45
}
```

## 🎨 Confidence Levels

The system uses confidence scores to indicate detection reliability:

| Score Range | Badge | Description | Recommended Use |
|------------|-------|-------------|-----------------|
| **≥ 0.80** | Very High | Fully reliable | ✅ Full automation |
| **0.65-0.79** | High | Safe for most cases | ✅ Automation with logging |
| **0.45-0.64** | Moderate | Proceed with caution | ⚠️ Manual verification |
| **< 0.45** | Low | Unreliable | ❌ Not recommended |

## 🛠️ Development

### File Overview

**`public/index.html`**
- Semantic HTML5 structure
- Two input tabs (GitHub URL / ZIP Upload)
- Results display sections
- Loading and error states

**`public/styles.css`**
- CSS custom properties (variables)
- Responsive grid layouts
- Smooth transitions and animations
- Card-based design system

**`public/app.js`**
- Event handling for forms and tabs
- Fetch API for backend communication
- Dynamic results rendering
- Real-time health check monitoring

**`serve.py`**
- Simple HTTP server for static files
- API request proxy to backend
- CORS headers support
- Error handling and logging

### Making Changes

1. **HTML Changes**: Edit `public/index.html`
2. **Style Changes**: Edit `public/styles.css`
3. **Logic Changes**: Edit `public/app.js`
4. **Server Changes**: Edit `serve.py`

Simply refresh your browser to see changes (no build step needed!)

## 🐳 Docker Deployment

You can deploy the frontend using Docker:

```bash
# Build the image
docker build -t project-detector-frontend .

# Run the container
docker run -p 3000:3000 -e BACKEND_URL=http://backend:8000 project-detector-frontend
```

## 📊 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

**Features used:**
- Fetch API
- CSS Grid & Flexbox
- CSS Custom Properties
- ES6 JavaScript (const, let, arrow functions, template literals)

## 🔒 Security Considerations

- ✅ No sensitive data stored in frontend
- ✅ CORS headers properly configured
- ✅ Input validation before API calls
- ✅ Error messages don't expose internal details
- ⚠️ HTTPS recommended for production
- ⚠️ Configure CORS allow_origins in production backend

## 🚀 Production Deployment

### Option 1: Python Server (Recommended for small scale)

```bash
# Start the server
python3 serve.py
```

### Option 2: Nginx (Recommended for production)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/public;
    index index.html;

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Option 3: Docker Compose

See `docker-compose.yml` in the project root.

## 🧪 Testing

### Manual Testing

1. **Health Check**: Open frontend, verify "API Online" status
2. **GitHub Scan**: Test with `https://github.com/facebook/react`
3. **ZIP Upload**: Upload a sample project ZIP file
4. **Confidence Slider**: Adjust threshold and rescan

### Quick Test Commands

```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Test scan endpoint
curl -X POST http://localhost:3000/api/scan \
  -F "github_url=https://github.com/facebook/react" \
  -F "min_confidence=0.5"
```

## 📝 Troubleshooting

### API shows "Offline"
- Verify backend is running on port 8000
- Check `BACKEND_URL` in `serve.py`
- Check firewall/network settings

### "Failed to scan repository"
- Verify GitHub URL is valid and public
- Check backend logs for errors
- Ensure min_confidence is between 0.0 and 1.0

### File upload not working
- Verify file is a valid ZIP archive
- Check file size (backend may have limits)
- Ensure ZIP contains project files

### Port 3000 already in use
- Change `PORT` in `serve.py`
- Or kill existing process: `kill $(lsof -t -i:3000)`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

See LICENSE file in the project root.

## 🔗 Related Documentation

- [Backend API Documentation](../API_DOCUMENTATION.md)
- [Main Project README](../README.md)
- [Deployment Guide](../DEPLOYMENT.md)

## 💡 Why Vanilla JavaScript?

We chose vanilla JavaScript over React/Vue/Angular because:

- ✅ **Zero build time** - No webpack, vite, or babel needed
- ✅ **No dependency hell** - No npm install, no node_modules
- ✅ **Universal compatibility** - Works everywhere, always
- ✅ **Lightning fast** - No framework overhead
- ✅ **Easy to understand** - Simple, readable code
- ✅ **Future-proof** - JavaScript won't change breaking APIs

Perfect for a focused, single-purpose application like this!

---

**Made with ❤️ using Vanilla JavaScript**
