# CodSoft Artificial Intelligence Internship Projects

Welcome to my **CodSoft Artificial Intelligence Internship** repository! This project hosts a collection of practical AI implementations completed during the internship program. It contains two main tasks, both featuring robust Python backend engines and interactive, responsive web-based user interfaces.

---

## 📂 Repository Structure

The repository is organized into distinct directories for each task:

```bash
CODSOFT/
├── Task1_Chatbot/        # Task 1: Rule-Based Chatbot with Personalities
│   ├── web/             # Frontend assets (HTML, CSS, JavaScript)
│   ├── chatbot.py       # Core rule-based dialog manager engine
│   ├── main.py          # Console interface & web launcher script
│   ├── server.py        # Custom API & HTTP server backend
│   └── test_chatbot.py  # Unit tests for conversation rules
│
└── Task2_TicTacToe/      # Task 2: Unbeatable Tic-Tac-Toe AI Game
    ├── web/             # Frontend assets (HTML, CSS, JavaScript)
    ├── game.py          # Minimax algorithm with Alpha-Beta pruning
    ├── main.py          # Console interface & web launcher script
    ├── server.py        # Custom API & HTTP server backend
    └── test_game.py     # Unit tests for Tic-Tac-Toe win check/moves
```

---

## 🤖 Task 1: Rule-Based Chatbot with Personalities

A multi-personality conversational assistant powered by regex-based pattern matching, stateful dialog flow management, and dynamic web interfaces.

### Features
*   **4 Distinct Personalities**:
    *   **Nova**: A polite, professional, and efficient virtual assistant.
    *   **Byte**: A geeky, code-loving, terminal-dwelling tech enthusiast.
    *   **Spike**: A witty, playfully sarcastic, and humorous companion.
    *   **Zen**: A calm, mindful, and peaceful guide focusing on inner balance.
*   **Interactive Features**: Supports greetings, small talk, custom math calculations, randomized personality-specific jokes, simulated weather forecasting, time/date queries, and context awareness (remembers user's name and tracks mood).
*   **Two Play Modes**: Full terminal terminal interface or beautiful web interface.
*   **Clean CSS & UI**: Responsive, modern glassmorphic chat bubble layout with transition effects.

### How to Run

1. Navigate to the chatbot directory:
   ```bash
   cd Task1_Chatbot
   ```
2. **Run in Web Mode** (launches local server and automatically opens browser):
   ```bash
   python main.py
   ```
3. **Run in Console Mode** (play directly inside the terminal):
   ```bash
   python main.py --console
   ```

---

## ❌ Task 2: Unbeatable Tic-Tac-Toe AI

A classic Tic-Tac-Toe game featuring an unbeatable AI opponent utilizing the **Minimax Algorithm with Alpha-Beta Pruning** to calculate the optimal move dynamically.

### Features
*   **Three Difficulty Levels**:
    *   **Easy**: Random selection of available moves.
    *   **Medium**: 60% optimal moves using Minimax, 40% random play.
    *   **Unbeatable**: Optimal mathematical move calculation via Minimax and Alpha-Beta pruning.
*   **Smart First-Move Optimization**: Hardcoded optimal start options (center or corners) to dramatically lower lookup times on an empty board.
*   **Modern Web GUI**: Sleek neon-themed design, smooth cell hover actions, responsive scaling, win/draw screen announcements, and real-time settings adjustments (difficulty, human symbol, starting player).

### How to Run

1. Navigate to the Tic-Tac-Toe directory:
   ```bash
   cd Task2_TicTacToe
   ```
2. **Run in Web Mode** (launches local server and automatically opens browser):
   ```bash
   python main.py
   ```
3. **Run in Console Mode** (play directly inside the terminal):
   ```bash
   python main.py --console
   ```

---

## 🧪 Testing

Both projects include custom testing suites to verify logic correctness:
*   Run Chatbot tests: `python Task1_Chatbot/test_chatbot.py`
*   Run Tic-Tac-Toe tests: `python Task2_TicTacToe/test_game.py`

---

## 🛠️ Tech Stack & Requirements
*   **Backend**: Python 3 (using standard libraries: `http.server`, `urllib`, `re`, `json`, `random`, `webbrowser`)
*   **Frontend**: Vanilla HTML5, Vanilla CSS3 (modern responsive styling), and Vanilla JavaScript (ES6+ async fetch API integration)
*   No external third-party dependencies required! Runs out-of-the-box on Windows, macOS, or Linux.
