import sys
import argparse
import webbrowser
import threading
import time
from server import run_server
from recommend import RecommendationEngine

ASCII_ART = r"""
______                                                 _   _             
| ___ \                                               | | (_)            
| |_/ /___  ___ ___  _ __ ___  _ __ ___   ___ _ __   _| |_ _  ___  _ __  
|    // _ \/ __/ _ \| '_ ` _ \| '_ ` _ \ / _ \ '_ \ / _` | |/ _ \| '_ \ 
| |\ \  __/ (_| (_) | | | | | | | | | | |  __/ | | | (_| | | (_) | | | |
\_| \_\___|\___\___/|_| |_| |_|_| |_| |_|\___|_| |_|\__,_|_|\___/|_| |_|
                                                                        
"""

def run_console_recommender():
    engine = RecommendationEngine()
    print(ASCII_ART)
    print("CodSoft Artificial Intelligence Internship — Task 4: Recommendation System")
    print("-------------------------------------------------------------------------\n")

    while True:
        print("Select recommendation strategy:")
        print("1. Content-Based Filtering (Recommend items similar to another item)")
        print("2. Collaborative Filtering (Recommend items based on other users' ratings)")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()

        if choice == '3':
            print("Exiting...")
            break
        elif choice == '1':
            print("\nDatabase Items:")
            for item in engine.all_items:
                print(f"  [{item['id']}] {item['title']} - {item['genre']}")
            
            item_id = input("\nEnter Item ID to query similarity: ").strip()
            if item_id not in engine.item_by_id:
                print("Error: Invalid Item ID.\n")
                continue
                
            recs, explanation = engine.get_content_recommendations(item_id)
            print(f"\nRecommendations for '{engine.item_by_id[item_id]['title']}':")
            for i, rec in enumerate(recs):
                print(f"  {i+1}. {rec['title']} (Cosine Similarity: {rec['score']:.4f})")
                print(f"     Genre: {rec['genre']}")
                print(f"     Desc : {rec['desc']}")
            print("-------------------------------------------------------------------------\n")
            
        elif choice == '2':
            print("\nUsers List:")
            for user in engine.users:
                print(f"  - {user}")
            
            user = input("\nEnter username to get recommendations: ").strip()
            if user not in engine.users:
                print("Error: User not found.\n")
                continue
                
            recs, explanation = engine.get_collaborative_recommendations(user)
            print(f"\nRecommendations for User '{user}':")
            if not recs:
                print("  No recommendations available (user has rated everything, or has no correlated peers).")
            for i, rec in enumerate(recs):
                print(f"  {i+1}. {rec['title']} (Predicted Rating: {rec['predicted_rating']:.1f}/5.0)")
                print(f"     Genre: {rec['genre']}")
                print(f"     Desc : {rec['desc']}")
            print("-------------------------------------------------------------------------\n")

def open_browser_delayed(url):
    time.sleep(0.8)
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="CodSoft Task 4: Recommendation System Launcher")
    parser.add_argument("--console", action="store_true", help="Launch in console-only mode")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    args = parser.parse_args()

    if args.console:
        run_console_recommender()
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
        print("CodSoft Artificial Intelligence Internship — Task 4: Recommendation System")
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
