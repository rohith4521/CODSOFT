import sys
import argparse
import webbrowser
import threading
import time
from server import run_server
from chatbot import Chatbot

# ANSI Escape codes for beautiful console mode formatting
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Colors
GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

PERSONALITY_COLORS = {
    "nova": BLUE,
    "byte": MAGENTA,
    "spike": YELLOW,
    "zen": GREEN
}
ASCII_ART = r"""
   ___  ___  ___   ___   ___  ___ _____ 
  / __|/ _ \|   \ / __| / _ \| __|_   _|
 | (__| (_) | |) |\___ \ | (_) | _|  | |  
  \___|\___/|___/ |___/  \___/|_|  |_|  
"""

def clean_markdown_for_terminal(text):
    """Translates simple markdown tags into terminal escape sequences."""
    # Bold **text** -> BOLD text
    text = re_sub_bold(text)
    # Italic *text* or _text_ -> UNDERLINE or italic-ish
    text = re_sub_italic(text)
    # Inline code `code` -> reverse color or gray
    text = re_sub_code(text)
    return text

def re_sub_bold(text):
    import re
    return re.sub(r'\*\*([^*]+)\*\*', BOLD + r'\1' + RESET, text)

def re_sub_italic(text):
    import re
    return re.sub(r'\*([^*]+)\*', UNDERLINE + r'\1' + RESET, text)

def re_sub_code(text):
    import re
    return re.sub(r'`([^`]+)`', GRAY + r'\1' + RESET, text)

def run_console_chat():
    """Runs a fully immersive colored CLI session."""
    chatbot = Chatbot()
    state = {}
    current_personality = "nova"

    print(f"{BOLD}{BLUE}{ASCII_ART}{RESET}")
    print(f"{BOLD}{WHITE}CodSoft Artificial Intelligence Internship — Task 1: Rule-Based Chatbot{RESET}")
    print(f"{GRAY}-------------------------------------------------------------------------{RESET}")
    print(f"Chatbot Engine initialized. Currently chatting with: {BOLD}{BLUE}Nova (Helpful Assistant){RESET}")
    print(f"Type {BOLD}/help{RESET} for special console commands or {BOLD}/exit{RESET} to close the chat.")
    print(f"{GRAY}-------------------------------------------------------------------------{RESET}\n")

    # Initial bot greeting simulation
    greeting, state = chatbot.process_message("hello", state, current_personality)
    bot_color = PERSONALITY_COLORS[current_personality]
    print(f"{BOLD}{bot_color}{current_personality.upper()}:{RESET} {greeting}\n")

    while True:
        try:
            # User input prompt
            user_input = input(f"{BOLD}{GREEN}YOU:{RESET} ").strip()
            if not user_input:
                continue

            # Command routing
            lower_input = user_input.lower()
            if lower_input == "/exit" or lower_input == "/quit":
                print(f"\n{BOLD}{bot_color}{current_personality.upper()}:{RESET} Goodbye! Closing console session.")
                break
                
            elif lower_input == "/help":
                print(f"\n{BOLD}{WHITE}=== CONSOLE COMMANDS ==={RESET}")
                print(f"  {BOLD}/exit{RESET} or {BOLD}/quit{RESET}   - Terminate the chatbot session.")
                print(f"  {BOLD}/clear{RESET}            - Clear conversation memory.")
                print(f"  {BOLD}/personality{RESET}     - See list of available bot personalities.")
                print(f"  {BOLD}/switch [name]{RESET}   - Switch bot personality (nova, byte, spike, zen).")
                print(f"  {BOLD}/state{RESET}            - Print current conversation memory state variables.")
                print(f"========================\n")
                continue
                
            elif lower_input == "/clear":
                state = {}
                print(f"\n{BOLD}{WHITE}Conversation memory wiped clean.{RESET}\n")
                continue
                
            elif lower_input == "/personality":
                print(f"\n{BOLD}{WHITE}=== CHATBOT PERSONALITIES ==={RESET}")
                for p, desc in chatbot.descriptions.items():
                    color = PERSONALITY_COLORS[p]
                    print(f"  {BOLD}{color}{p.upper()}{RESET} - {desc}")
                print(f"=============================\n")
                continue
                
            elif lower_input.startswith("/switch "):
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1:
                    new_p = parts[1].strip().lower()
                    if new_p in PERSONALITY_COLORS:
                        current_personality = new_p
                        bot_color = PERSONALITY_COLORS[current_personality]
                        print(f"\n{GRAY}System: Bot personality switched to {BOLD}{bot_color}{current_personality.upper()}{RESET}.\n")
                        # Welcome prompt for new personality
                        welcome_msg = chatbot.descriptions[current_personality]
                        print(f"{BOLD}{bot_color}{current_personality.upper()}:{RESET} Hi, I'm now active. {welcome_msg}\n")
                    else:
                        print(f"\n{RED}Error: Unknown personality '{new_p}'. Options: nova, byte, spike, zen.{RESET}\n")
                else:
                    print(f"\n{RED}Usage: /switch [nova|byte|spike|zen]{RESET}\n")
                continue
                
            elif lower_input == "/state":
                print(f"\n{BOLD}{WHITE}=== MEMORY STATE ==={RESET}")
                print(f"  User Name:      {state.get('name')}")
                print(f"  Current Topic:  {state.get('topic')}")
                print(f"  Message Turns:  {state.get('messages_count')}")
                print(f"====================\n")
                continue
                
            elif user_input.startswith("/"):
                print(f"\n{RED}Unknown command: {user_input}. Type /help for assistance.{RESET}\n")
                continue

            # Process standard chat message
            print(f"{GRAY}* thinking... *{RESET}", end="\r")
            time.sleep(0.3)  # Tiny artificial delay for realism
            sys.stdout.write("\033[K") # Clear the line

            reply, state = chatbot.process_message(user_input, state, current_personality)
            formatted_reply = clean_markdown_for_terminal(reply)
            
            print(f"{BOLD}{bot_color}{current_personality.upper()}:{RESET} {formatted_reply}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{BOLD}{bot_color}{current_personality.upper()}:{RESET} Connection interrupted. Goodbye!")
            break

def open_browser_delayed(url):
    """Wait briefly for the server socket to open, then launch the default browser."""
    time.sleep(0.8)
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="CodSoft Task 1: Rule-Based Chatbot Launcher")
    parser.add_argument("--console", action="store_true", help="Launch directly in Console/CLI Mode")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    args = parser.parse_args()

    if args.console:
        run_console_chat()
    else:
        # Run server mode
        httpd, port = run_server(args.port)
        if not httpd:
            sys.exit(1)
            
        local_url = f"http://localhost:{port}/"
        
        # Start browser thread
        browser_thread = threading.Thread(target=open_browser_delayed, args=(local_url,))
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"\n{BOLD}{BLUE}{ASCII_ART}{RESET}")
        print(f"{BOLD}{WHITE}CodSoft Artificial Intelligence Internship — Task 1: Rule-Based Chatbot{RESET}")
        print(f"{GRAY}-------------------------------------------------------------------------{RESET}")
        print(f"Web server successfully started.")
        print(f"Address: {BOLD}{CYAN}{local_url}{RESET}")
        print(f"To chat, simply use the browser tab that opened automatically.")
        print(f"To run in the terminal instead, terminate this process and run: {BOLD}python main.py --console{RESET}")
        print(f"Shutdown: Press {BOLD}Ctrl+C{RESET} in this terminal to stop the server.")
        print(f"{GRAY}-------------------------------------------------------------------------{RESET}\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server. Goodbye!")
            httpd.server_close()

if __name__ == "__main__":
    main()
