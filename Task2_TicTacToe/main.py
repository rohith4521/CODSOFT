import sys
import argparse
import webbrowser
import threading
import time
from server import run_server
from game import TicTacToeGame

# ANSI colors for console mode
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

ASCII_ART = r"""
 _____ _        _____            _____             
|_   _(_) ___  |_   _|_ _  ___  |_   _|___  ___ ___ 
  | | | |/ __|   | |/ _` |/ __|   | |/ _ \/ _ \___|
  | | | | (__    | | (_| | (__    | |  __/  __/   
  |_| |_|\___|   |_|\__,_|\___|   |_|\___|\___|   
"""

def print_board(board):
    """Draws a beautiful colored board with index helpers next to it."""
    # Build helper cell indices
    helpers = [f"{GRAY}{i+1}{RESET}" if board[i] == ' ' else ' ' for i in range(9)]
    
    # Format symbol colors
    colored = []
    for cell in board:
        if cell == 'X':
            colored.append(f"{BOLD}{CYAN}X{RESET}")
        elif cell == 'O':
            colored.append(f"{BOLD}{MAGENTA}O{RESET}")
        else:
            colored.append(' ')
            
    print("\n      BOARD             GUIDE (Keys 1-9)")
    print(f"  {colored[0]} {GRAY}|{RESET} {colored[1]} {GRAY}|{RESET} {colored[2]}         {helpers[0]} {GRAY}|{RESET} {helpers[1]} {GRAY}|{RESET} {helpers[2]}")
    print(f" {GRAY}---+---+---       ---+---+---{RESET}")
    print(f"  {colored[3]} {GRAY}|{RESET} {colored[4]} {GRAY}|{RESET} {colored[5]}         {helpers[3]} {GRAY}|{RESET} {helpers[4]} {GRAY}|{RESET} {helpers[5]}")
    print(f" {GRAY}---+---+---       ---+---+---{RESET}")
    print(f"  {colored[6]} {GRAY}|{RESET} {colored[7]} {GRAY}|{RESET} {colored[8]}         {helpers[6]} {GRAY}|{RESET} {helpers[7]} {GRAY}|{RESET} {helpers[8]}\n")

def run_console_game():
    game = TicTacToeGame()
    board = [' '] * 9
    
    print(f"{BOLD}{CYAN}{ASCII_ART}{RESET}")
    print(f"{BOLD}{WHITE}CodSoft Artificial Intelligence Internship — Task 2: Tic-Tac-Toe AI{RESET}")
    print(f"{GRAY}-------------------------------------------------------------------------{RESET}\n")

    # 1. Setup Symbol
    while True:
        symbol_input = input(f"{BOLD}Choose your symbol (X or O) [Default X]:{RESET} ").strip().upper()
        if not symbol_input:
            human_symbol = 'X'
            break
        if symbol_input in ['X', 'O']:
            human_symbol = symbol_input
            break
        print(f"{RED}Invalid input. Please type 'X' or 'O'.{RESET}")

    ai_symbol = 'O' if human_symbol == 'X' else 'X'
    print(f"You are {BOLD}{CYAN}{human_symbol}{RESET}. AI is {BOLD}{MAGENTA}{ai_symbol}{RESET}.\n")

    # 2. Setup Difficulty
    while True:
        diff_input = input(f"{BOLD}Choose difficulty (easy, medium, unbeatable) [Default unbeatable]:{RESET} ").strip().lower()
        if not diff_input:
            difficulty = 'unbeatable'
            break
        if diff_input in ['easy', 'medium', 'unbeatable']:
            difficulty = diff_input
            break
        print(f"{RED}Invalid option. Type 'easy', 'medium', or 'unbeatable'.{RESET}")
    
    # 3. Setup Starter
    while True:
        start_input = input(f"{BOLD}Who should play first? (human or ai) [Default human]:{RESET} ").strip().lower()
        if not start_input:
            starter = 'human'
            break
        if start_input in ['human', 'ai']:
            starter = start_input
            break
        print(f"{RED}Invalid input. Type 'human' or 'ai'.{RESET}")

    print(f"\n{GREEN}Game started! Good luck.{RESET}")
    
    # Turn execution
    current_player = starter
    
    while True:
        print_board(board)
        winner = game.check_winner(board)
        
        if winner:
            if winner == 'Tie':
                print(f"{BOLD}{YELLOW}Game Over: It's a Tie!{RESET}\n")
            elif winner == human_symbol:
                print(f"{BOLD}{GREEN}Game Over: Congratulations! You won!{RESET}\n")
            else:
                print(f"{BOLD}{RED}Game Over: AI won. Unbeatable logic prevails!{RESET}\n")
            break

        if current_player == 'human':
            # Human Turn
            while True:
                try:
                    move_key = input(f"{BOLD}{CYAN}YOUR TURN ({human_symbol}) - Enter square (1-9):{RESET} ").strip()
                    if move_key.lower() == 'exit' or move_key.lower() == 'quit':
                        print(f"\n{GRAY}Exiting game...{RESET}")
                        return
                    
                    val = int(move_key)
                    if 1 <= val <= 9:
                        idx = val - 1
                        if board[idx] == ' ':
                            board[idx] = human_symbol
                            break
                        else:
                            print(f"{RED}Square {val} is already occupied.{RESET}")
                    else:
                        print(f"{RED}Please enter a number between 1 and 9.{RESET}")
                except ValueError:
                    print(f"{RED}Invalid input. Enter a number 1-9 or type 'exit'.{RESET}")
            current_player = 'ai'
        else:
            # AI Turn
            print(f"{GRAY}* AI is computing move... *{RESET}")
            time.sleep(0.5) # Realism pause
            ai_move = game.get_ai_move(board, ai_symbol, difficulty)
            board[ai_move] = ai_symbol
            print(f"{BOLD}{MAGENTA}AI played on square {ai_move + 1}.{RESET}")
            current_player = 'human'

def open_browser_delayed(url):
    time.sleep(0.8)
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="CodSoft Task 2: Tic-Tac-Toe AI Launcher")
    parser.add_argument("--console", action="store_true", help="Launch directly in console-only mode")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    args = parser.parse_args()

    if args.console:
        run_console_game()
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
        
        print(f"\n{BOLD}{CYAN}{ASCII_ART}{RESET}")
        print(f"{BOLD}{WHITE}CodSoft Artificial Intelligence Internship — Task 2: Tic-Tac-Toe AI{RESET}")
        print(f"{GRAY}-------------------------------------------------------------------------{RESET}")
        print(f"Web server successfully started.")
        print(f"Address: {BOLD}{CYAN}{local_url}{RESET}")
        print(f"To play, simply use the browser tab that opened automatically.")
        print(f"To play in the terminal instead, terminate this and run: {BOLD}python main.py --console{RESET}")
        print(f"Shutdown: Press {BOLD}Ctrl+C{RESET} in this terminal to stop the server.")
        print(f"{GRAY}-------------------------------------------------------------------------{RESET}\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server. Goodbye!")
            httpd.server_close()

if __name__ == "__main__":
    main()
