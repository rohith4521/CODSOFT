import http.server
import json
import os
import urllib.parse
from recommend import RecommendationEngine

# Instantiate engine
engine = RecommendationEngine()

class RecommendHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
        parsed_path = urllib.parse.urlparse(self.path).path
        
        if parsed_path == '/':
            file_path = os.path.join(base_dir, 'index.html')
        elif parsed_path == '/api/items':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "movies": engine.movies,
                "books": engine.books
            }).encode('utf-8'))
            return
        elif parsed_path == '/api/users':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # Return usernames and their ratings
            self.wfile.write(json.dumps({
                "users": list(engine.users.keys()),
                "ratings": engine.users
            }).encode('utf-8'))
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

        if self.path == '/api/content':
            try:
                data = json.loads(post_data.decode('utf-8'))
                item_id = data.get('item_id', '')
                if not item_id:
                    raise ValueError("item_id is required.")
                
                recs, explanation = engine.get_content_recommendations(item_id)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "recommendations": recs,
                    "explanation": explanation
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        elif self.path == '/api/collaborative':
            try:
                data = json.loads(post_data.decode('utf-8'))
                username = data.get('username', '')
                if not username:
                    raise ValueError("username is required.")
                
                recs, explanation = engine.get_collaborative_recommendations(username)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "recommendations": recs,
                    "explanation": explanation
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        elif self.path == '/api/rate':
            try:
                data = json.loads(post_data.decode('utf-8'))
                username = data.get('username', '')
                item_id = data.get('item_id', '')
                rating = int(data.get('rating', 0))
                
                if not username or not item_id:
                    raise ValueError("username and item_id are required.")
                
                if username not in engine.users:
                    # Create new user
                    engine.users[username] = {}
                
                engine.users[username][item_id] = rating
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "ratings": engine.users[username]
                }).encode('utf-8'))
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
            httpd = http.server.HTTPServer(('', current_port), RecommendHTTPRequestHandler)
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
