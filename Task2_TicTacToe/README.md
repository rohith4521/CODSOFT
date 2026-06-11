# Task 2: Unbeatable Tic-Tac-Toe AI Game

An interactive, responsive Tic-Tac-Toe game featuring an unbeatable AI opponent driven by the **Minimax Algorithm with Alpha-Beta Pruning** for perfect mathematical decision-making.

---

## 🚀 Key Features

*   **🧠 Unbeatable AI Engine**: Fully implemented Minimax algorithm. The AI evaluates possible future moves, scores them, and uses Alpha-Beta pruning to optimize recursion speed, guaranteeing it never loses at the highest difficulty.
*   **📊 Three Difficulty Modes**:
    *   **Easy**: Random selection of available spaces.
    *   **Medium**: 60% optimal moves using Minimax, 40% random play.
    *   **Unbeatable**: Strict Minimax execution with Alpha-Beta pruning.
*   **⚡ First-Move Optimization**: Hardcoded first-turn responses (center or corners) to dramatically lower lookup times on an empty board.
*   **💻 Dual Interface Modes**:
    *   **Web GUI**: Premium glassmorphic neon UI with dynamic win/tie banners and hover effects.
    *   **Console Mode**: ASCII-art guide board playable in the terminal.

---

## 🛠️ Tech Stack

*   **Backend**: Python 3 (standard libraries: `http.server`, `urllib.parse`, `json`, `random`, `webbrowser`, `threading`, `time`)
*   **Frontend**: Vanilla HTML5, Vanilla CSS3 (modern neon/dark mode theme), and Vanilla JavaScript (ES6+ async fetch API integration)

---

## 📦 How to Run

1.  Navigate to the Tic-Tac-Toe project directory:
    ```powershell
    cd Task2_TicTacToe
    ```
2.  **Start in Web Mode** (launches local server and automatically opens browser):
    ```powershell
    python main.py
    ```
3.  **Start in Console Mode** (interact directly in the terminal):
    ```powershell
    python main.py --console
    ```

---

## 🧪 Testing

To run the custom test suite validating game states (win checking, tie checking, AI moves):
```powershell
python test_game.py
```
