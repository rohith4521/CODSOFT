import sys
import argparse
import webbrowser
import threading
import time
import os
import base64
from server import run_server
from face_engine import FaceEngine

ASCII_ART = r"""
 ______               ______      _            _   _             
|  ___|              |  _  \    | |          | | (_)            
| |_ __ _  ___ ___   | | | | ___| |_ ___  ___| |_ _  ___  _ __  
|  _/ _` |/ __/ _ \  | | | |/ _ \ __/ _ \/ __| __| |/ _ \| '_ \ 
| || (_| | (_|  __/  | |/ /|  __/ ||  __/ (__| |_| | (_) | | | |
\_| \__,_|\___\___|  |___/  \___|\__\___|\___|\__|_|\___/|_| |_|
                                                                
"""

def run_console_detector():
    try:
        engine = FaceEngine()
    except Exception as e:
        print(f"Error initializing face detector: {e}")
        print("Please ensure 'opencv-python' is installed by running: pip install opencv-python")
        sys.exit(1)

    print(ASCII_ART)
    print("CodSoft Artificial Intelligence Internship — Task 5: Face Detection & Recognition")
    print("-------------------------------------------------------------------------\n")

    while True:
        path = input("Enter path to an image file (or 'exit' to quit): ").strip().strip('"')
        if path.lower() in ['exit', 'quit']:
            print("Exiting...")
            break
            
        if not path:
            continue
            
        if not os.path.exists(path):
            print(f"Error: File '{path}' does not exist. Please enter a valid path.")
            continue

        try:
            with open(path, 'rb') as f:
                img_data = f.read()
            
            print("\n* Processing face detection using Haar Cascades... *")
            time.sleep(0.5)
            
            faces, frame_b64 = engine.detect_faces(img_data)
            
            print(f"Success! Detected {len(faces)} face(s).")
            for i, face in enumerate(faces):
                print(f"  Face {i+1}: Coordinates: (x:{face['x']}, y:{face['y']}, w:{face['w']}, h:{face['h']})")
                print(f"          Identity   : {face['name']} (Similarity Score: {face['confidence']*100:.1f}%)")

            # Save result image
            header, b64_raw = frame_b64.split(',')
            output_path = os.path.join(os.path.dirname(os.path.abspath(path)), "detected_" + os.path.basename(path))
            with open(output_path, 'wb') as f_out:
                f_out.write(base64.b64decode(b64_raw))
            print(f"\nResult image with bounding boxes saved to: {output_path}")
            print("-------------------------------------------------------------------------\n")
            
        except Exception as e:
            print("Error processing image:", e)

def open_browser_delayed(url):
    time.sleep(0.8)
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="CodSoft Task 5: Face Detection & Recognition Launcher")
    parser.add_argument("--console", action="store_true", help="Launch in console-only mode")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    args = parser.parse_args()

    if args.console:
        run_console_detector()
    else:
        # Run Server Mode
        httpd, port = run_server(args.port)
        if not httpd:
            sys.exit(1)
            
        local_url = f"http://localhost:{port}/"
        
        # Start browser thread
        browser_thread = threading.Thread(target=open_browser_delayed, args=(local_url,))
        browser_thread.daemon = True
        browser_thread.start()
        
        print(ASCII_ART)
        print("CodSoft Artificial Intelligence Internship — Task 5: Face Detection & Recognition")
        print("-------------------------------------------------------------------------")
        print(f"Web server successfully started.")
        print(f"Address: {local_url}")
        print(f"To open, use the browser tab that opened automatically.")
        print(f"To play in the terminal instead, terminate this and run: python main.py --console")
        print(f"Shutdown: Press Ctrl+C in this terminal to stop the server.")
        print("-------------------------------------------------------------------------\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server. Goodbye!")
            httpd.server_close()

if __name__ == "__main__":
    main()
