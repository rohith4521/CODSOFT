import http.server
import json
import os
import urllib.parse
from game import TicTacToeGame

# Global game engine instance
game_instance = TicTacToeGame()

class TicTacToeHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to keep the CLI clean
        pass

    def do_GET(self):
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
        parsed_path = urllib.parse.urlparse(self.path).path
        
        if parsed_path == '/':
            file_path = os.path.join(base_dir, 'index.html')
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
            elif ext == '.json':
                content_type = 'application/json'

            self.send_header('Content-Type', content_type)
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        if self.path == '/api/move':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                board = data.get('board', [' '] * 9)
                ai_symbol = data.get('ai_symbol', 'O')
                difficulty = data.get('difficulty', 'unbeatable')
                
                # Check current status before making a move
                initial_winner = game_instance.check_winner(board)
                if initial_winner is not None:
                    # Game is already over
                    response_payload = {
                        'move': -1,
                        'board': board,
                        'winner': initial_winner
                    }
                else:
                    # Calculate AI move
                    ai_move = game_instance.get_ai_move(board, ai_symbol, difficulty)
                    
                    # Update board
                    board[ai_move] = ai_symbol
                    
                    # Check status after AI move
                    final_winner = game_instance.check_winner(board)
                    
                    response_payload = {
                        'move': ai_move,
                        'board': board,
                        'winner': final_winner
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
    max_retries = 10
    httpd = None
    current_port = port
    
    for i in range(max_retries):
        try:
            httpd = http.server.HTTPServer(('', current_port), TicTacToeHTTPRequestHandler)
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
