#!/usr/bin/env python3
"""
Simple HTTP server with API proxy for serving the frontend application
"""
import http.server
import socketserver
import os
import urllib.request
import urllib.error
import json

PORT = 3000
DIRECTORY = "public"
BACKEND_URL = "http://localhost:8000"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        # Proxy API requests to backend
        if self.path.startswith('/api/'):
            self.proxy_request('GET')
        else:
            super().do_GET()
    
    def do_POST(self):
        # Proxy API requests to backend
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(501, "Unsupported method ('POST')")
    
    def proxy_request(self, method):
        """Proxy the request to the backend API"""
        try:
            # Read request body for POST
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Build backend URL
            backend_url = f"{BACKEND_URL}{self.path}"
            
            # Create request
            if method == 'GET':
                req = urllib.request.Request(backend_url, method='GET')
            else:
                req = urllib.request.Request(backend_url, data=body, method='POST')
                # Copy content-type header
                if 'Content-Type' in self.headers:
                    req.add_header('Content-Type', self.headers['Content-Type'])
            
            # Send request to backend
            with urllib.request.urlopen(req) as response:
                # Send response to client
                self.send_response(response.status)
                
                # Copy headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Copy body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            # Forward HTTP errors from backend
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            # Handle connection errors
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                "detail": f"Backend service unavailable: {str(e)}"
            })
            self.wfile.write(error_response.encode())

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"✅ Frontend server running at: http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}/")
        print(f"🔗 Proxying /api/* requests to: {BACKEND_URL}")
        print(f"🛑 Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
