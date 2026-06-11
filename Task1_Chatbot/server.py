import http.server
import json
import os
import urllib.parse
from chatbot import Chatbot

# Global instance of chatbot
chatbot_instance = Chatbot()

class ChatbotHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default server console logging to keep terminal output clean and beautiful
        pass

    def do_GET(self):
        # Determine the base directory of the web files
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
        
        # Sanitize path to prevent directory traversal
        parsed_path = urllib.parse.urlparse(self.path).path
        if parsed_path == '/':
            file_path = os.path.join(base_dir, 'index.html')
        else:
            # Strip leading slash and join
            file_path = os.path.join(base_dir, parsed_path.lstrip('/'))

        # Check if the file is within the base directory (prevent path traversal)
        if not os.path.abspath(file_path).startswith(os.path.abspath(base_dir)):
            self.send_error(403, "Access Denied")
            return

        # Check if file exists and is a file
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            
            # Determine content type
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
            elif ext == '.json':
                content_type = 'application/json'

            self.send_header('Content-Type', content_type)
            self.end_headers()

            # Write file content
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        if self.path == '/api/chat':
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                personality = data.get('personality', 'nova')
                state = data.get('state', {})
                
                # Process the message using our Chatbot class
                response_text, updated_state = chatbot_instance.process_message(message, state, personality)
                
                # Create response payload
                response_payload = {
                    'response': response_text,
                    'state': updated_state
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response_payload).encode('utf-8'))
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint Not Found")

def run_server(port=8000):
    server_address = ('', port)
    
    # Simple retry logic to find an available port
    max_retries = 10
    httpd = None
    current_port = port
    
    for i in range(max_retries):
        try:
            httpd = http.server.HTTPServer(('', current_port), ChatbotHTTPRequestHandler)
            break
        except OSError as e:
            if e.errno == 98 or e.errno == 10048:  # Port already in use (Linux/Windows)
                print(f"Port {current_port} is already in use. Retrying on port {current_port + 1}...")
                current_port += 1
            else:
                raise e

    if not httpd:
        print("Could not find an available port to run the server.")
        return None, None

    return httpd, current_port
