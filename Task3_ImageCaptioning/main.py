import sys
import argparse
import webbrowser
import threading
import time
import base64
import os
from server import run_server
from caption_engine import CaptionEngine

ASCII_ART = r"""
 _____                               _____             _   _             _             
|_   _|                             /  __ \           | | (_)           (_)            
  | | _ __ ___   __ _  __ _  ___    | /  \/ __ _ _ __ | |_ _  ___  _ __  _ _ __   __ _  
  | || '_ ` _ \ / _` |/ _` |/ _ \   | |    / _` | '_ \| __| |/ _ \| '_ \| | '_ \ / _` | 
 _| || | | | | | (_| | (_| |  __/   | \__/\ (_| | |_) | |_| | (_) | | | | | | | | (_| | 
 \___/_| |_| |_|\__,_|\__, |\___|    \____/\__,_| .__/ \__|_|\___/|_| |_|_|_| |_|\__, | 
                       __/ |                    | |                               __/ | 
                      |___/                     |_|                              |___/  
"""

def run_console_captioner():
    engine = CaptionEngine()
    print(ASCII_ART)
    print("CodSoft Artificial Intelligence Internship — Task 3: Image Captioning AI")
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
            
            b64_data = base64.b64encode(img_data).decode('utf-8')
            
            print("\n* Simulating CNN visual feature extraction (VGG/ResNet) *")
            time.sleep(0.5)
            features = engine.generate_feature_maps(b64_data)
            if "error" in features:
                print("Error extracting features:", features["error"])
                continue
            
            print("- Layer 1 (Edges) map generated successfully.")
            print("- Layer 2 (Textures) map generated successfully.")
            print("- Layer 3 (Structural Parts) map generated successfully.")
            print("- Layer 4 (Attention Activation Heatmap) map generated successfully.")
            
            # Predict a mock caption for console mode
            mock_captions = [
                "a brown dog running through a grassy field",
                "a clean kitchen with steel appliances and white cabinets",
                "a group of people gathering in front of a building",
                "an old vintage car parked on a city street",
                "a cozy living room with a fireplace and bookshelf",
                "a small gray cat sleeping on a soft pillow"
            ]
            caption = random_choice_from_path(path, mock_captions)
            
            print(f"\n[Generated Caption]: {caption.upper()}")
            
            print("\n* Simulating LSTM Sequence Token Generator step-by-step *")
            time.sleep(0.5)
            trace = engine.simulate_lstm_trace(caption)
            for step in trace:
                print(f"  Step {step['step']}: Context: '{step['context']}'")
                print("    Next word probabilities:")
                for cand in step['predictions']:
                    indicator = "<- SELECTED" if cand['word'] == step['selected'] else ""
                    print(f"      - {cand['word']:<10}: {cand['prob']*100:.1f}% {indicator}")
                time.sleep(0.3)
            print("-------------------------------------------------------------------------\n")
            
        except Exception as e:
            print("Error processing image:", e)

def random_choice_from_path(path, options):
    # Deterministic choice based on path hash
    val = sum(ord(c) for c in os.path.basename(path))
    return options[val % len(options)]

def open_browser_delayed(url):
    time.sleep(0.8)
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="CodSoft Task 3: Image Captioning AI")
    parser.add_argument("--console", action="store_true", help="Launch in console-only mode")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    args = parser.parse_args()

    if args.console:
        run_console_captioner()
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
        print("CodSoft Artificial Intelligence Internship — Task 3: Image Captioning AI")
        print("-------------------------------------------------------------------------")
        print(f"Web server successfully started.")
        print(f"Address: {local_url}")
        print(f"To play, simply use the browser tab that opened automatically.")
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
