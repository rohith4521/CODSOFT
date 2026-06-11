# Task 1: Rule-Based Chatbot with Personalities

A conversational assistant built with Python and Vanilla JavaScript featuring stateful dialog flow management, regex-based pattern matching, and multiple interactive personalities.

---

## 🚀 Key Features

*   **🎭 4 Distinct Personalities**:
    *   **Nova (Default)**: Polite, professional, and efficient virtual assistant.
    *   **Byte**: Geeky, terminal-dwelling tech enthusiast.
    *   **Spike**: Playfully sarcastic, witty, and humorous companion.
    *   **Zen**: Calm, mindful, and peaceful guide focusing on inner balance.
*   **💬 Context-Aware Conversation Rules**:
    *   Greeting and exit handlers tailored to each personality.
    *   Name memory (remembers user introduction and personalizes replies).
    *   Basic math engine (addition, subtraction, multiplication, division, modulo).
    *   Personality-specific random joke database.
    *   Simulated local weather forecast query.
    *   Time & date queries.
    *   User mood/feeling detection with dynamic support/empathy.
*   **💻 Dual Interface Modes**:
    *   **Web GUI**: Responsive, modern glassmorphic chat interface.
    *   **Console Mode**: Play directly inside your CLI.

---

## 🛠️ Tech Stack

*   **Backend**: Python 3 (standard libraries: `http.server`, `urllib.parse`, `re`, `json`, `random`, `webbrowser`, `datetime`)
*   **Frontend**: Vanilla HTML5, Vanilla CSS3 (modern glassmorphism design), and Vanilla JavaScript (ES6+ async fetch API integration)

---

## 📦 How to Run

1.  Navigate to the chatbot project directory:
    ```powershell
    cd Task1_Chatbot
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

To run the custom test suite validating conversational rule pathways:
```powershell
python test_chatbot.py
```
