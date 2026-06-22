import http.server
import json
import os
import base64
import urllib.parse
from face_engine import FaceEngine

# Instantiate single face engine
engine = FaceEngine()

class FaceHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
        parsed_path = urllib.parse.urlparse(self.path).path
        
        if parsed_path == '/':
            file_path = os.path.join(base_dir, 'index.html')
        elif parsed_path == '/api/profiles':
            profiles = []
            # Gather registered profiles
            for name in engine.registered_faces.keys():
                filepath = os.path.join(engine.db_dir, f"{name}.png")
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        data = base64.b64encode(f.read()).decode('utf-8')
                        profiles.append({
                            "name": name,
                            "img": "data:image/png;base64," + data
                        })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"profiles": profiles}).encode('utf-8'))
            return
        else:
            file_path = os.path.join(base_dir, parsed_path.lstrip('/'))

        # Check path traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(base_dir)):
            self.send_error(403, "Access Denied")
            return

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            _, ext = os.path.splitext(file_path)
            content_type = 'text/plain'
            if ext == '.html':
                content_type = 'text/html'
            elif ext == '.css':
                content_type = 'text/css'
            elif ext == '.js':
                content_type = 'application/javascript'
            elif ext == '.png':
                content_type = 'image/png'
            elif ext == '.ico':
                content_type = 'image/x-icon'

            self.send_header('Content-Type', content_type)
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        if self.path == '/api/detect':
            try:
                data = json.loads(post_data.decode('utf-8'))
                image_b64 = data.get('image', '')
                if not image_b64:
                    raise ValueError("image field is required.")
                
                # Convert base64 to raw bytes
                if ',' in image_b64:
                    image_b64 = image_b64.split(',')[1]
                
                image_bytes = base64.b64decode(image_b64)
                
                faces, frame_b64 = engine.detect_faces(image_bytes)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "faces": faces,
                    "frame": frame_b64
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        elif self.path == '/api/register':
            try:
                data = json.loads(post_data.decode('utf-8'))
                name = data.get('name', '').strip()
                crop_b64 = data.get('crop', '')
                
                if not name or not crop_b64:
                    raise ValueError("name and crop base64 fields are required.")
                
                engine.register_face(name, crop_b64)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint Not Found")

def run_server(port=8000):
    max_retries = 10
    httpd = None
    current_port = port
    
    for i in range(max_retries):
        try:
            httpd = http.server.HTTPServer(('', current_port), FaceHTTPRequestHandler)
            break
        except OSError as e:
            if e.errno == 98 or e.errno == 10048:
                print(f"Port {current_port} is already in use. Retrying on port {current_port + 1}...")
                current_port += 1
            else:
                raise e

    if not httpd:
        print("Could not find an available port to run the server.")
        return None, None

    return httpd, current_port
