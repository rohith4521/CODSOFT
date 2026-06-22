# CodSoft Artificial Intelligence Internship Projects

Welcome to my **CodSoft Artificial Intelligence Internship** repository! This repository hosts a collection of practical AI implementations completed during the internship program. It contains five tasks, all featuring robust Python backend engines and interactive, responsive web-based user interfaces.

---

## 📂 Repository Structure

The repository is organized into distinct directories for each task:

```bash
CODSOFT/
├── Task1_Chatbot/              # Task 1: Rule-Based Chatbot with Personalities
│   ├── web/                    # Chatbot Web GUI (HTML, CSS, JS)
│   ├── chatbot.py              # Rule-Based Dialog Manager Engine
│   ├── main.py                 # Chatbot launcher (Console + Web)
│   └── test_chatbot.py         # Chatbot unit tests
│
├── Task2_TicTacToe/            # Task 2: Unbeatable Tic-Tac-Toe AI Game
│   ├── web/                    # Game Web GUI (HTML, CSS, JS)
│   ├── game.py                 # Minimax with Alpha-Beta Pruning Logic
│   ├── main.py                 # Game launcher (Console + Web)
│   └── test_game.py            # Game unit tests
│
├── Task3_ImageCaptioning/      # Task 3: Image Captioning AI Dashboard
│   ├── web/                    # Dashboard Web GUI (HTML, CSS, JS)
│   ├── caption_engine.py       # Simulated CNN Feature & LSTM Trace Engine
│   ├── main.py                 # Captioner launcher (Console + Web)
│   └── test_caption.py         # Captioner unit tests
│
├── Task4_RecommendationSystem/ # Task 4: Content & Collaborative Recommender
│   ├── web/                    # Dashboard Web GUI (HTML, CSS, JS)
│   ├── recommend.py            # TF-IDF, Cosine Similarity & Pearson CF Math
│   ├── main.py                 # Recommender launcher (Console + Web)
│   └── test_recommend.py       # Recommender unit tests
│
└── Task5_FaceDetection/        # Task 5: Face Detection & Recognition Profile Manager
    ├── web/                    # Live Scanner Web GUI (HTML, CSS, JS)
    ├── face_engine.py          # OpenCV Haar Cascades + Cosine Similarity matching
    ├── main.py                 # FaceID launcher (Console + Web)
    └── test_face.py            # FaceID unit tests
```

---

## 📖 Tasks Overview

| Task | Project Name | AI & Algorithm Core | Key Web GUI Features |
| :--- | :--- | :--- | :--- |
| **Task 1** | **Multi-Personality Chatbot** | Stateful dialog manager & Regex parsing | Glassmorphism chat bubble interface, 4 voice modes |
| **Task 2** | **Unbeatable Tic-Tac-Toe** | Minimax Algorithm + Alpha-Beta Pruning | Neon dark mode grid, real-time difficulty selectors |
| **Task 3** | **Image Captioning AI** | Client-side Transformers.js (BLIP/ViT-GPT2) + CNN-LSTM simulator | Drag-and-drop file upload, CNN filter layer viewer, LSTM step trace |
| **Task 4** | **Recommendation System** | TF-IDF Cosine Similarity & Pearson User Correlation from scratch | Dynamic rating sliders, TF-IDF weights overlap math table, peer similarity graph |
| **Task 5** | **Face Detection & Recognition** | OpenCV Haar Cascades & Facial Grayscale Descriptor match | HTML5 webcam live capture, scan overlay sweep, crops grid, save name modal |

---

## 🛠️ Global Requirements & Setup

This repository uses **Python 3** and minimal, lightweight dependencies. No heavy machine learning frameworks (like PyTorch or TensorFlow) are required locally!

### Installation
Install dependencies (OpenCV and NumPy) using `pip`:
```powershell
pip install -r requirements.txt
```

---

## 📦 How to Run the Projects

Each project supports two execution modes: **Web Mode** (which hosts a local server and automatically opens a browser GUI) and **Console Mode** (which runs directly in the terminal).

### 🤖 Run Task 1: Chatbot
```powershell
cd Task1_Chatbot
python main.py             # Web Mode (Default)
python main.py --console   # Console Mode
```

### ❌ Run Task 2: Tic-Tac-Toe AI
```powershell
cd Task2_TicTacToe
python main.py             # Web Mode (Default)
python main.py --console   # Console Mode
```

### 👁️‍🗨️ Run Task 3: Image Captioning AI
```powershell
cd Task3_ImageCaptioning
python main.py             # Web Mode (Default)
python main.py --console   # Console Mode
```

### 🎯 Run Task 4: Recommendation System
```powershell
cd Task4_RecommendationSystem
python main.py             # Web Mode (Default)
python main.py --console   # Console Mode
```

### 👤 Run Task 5: Face Detection & Recognition
```powershell
cd Task5_FaceDetection
python main.py             # Web Mode (Default)
python main.py --console   # Console Mode
```

---

## 🧪 Testing Suite
You can validate the backend algorithms by running unit tests in their respective directories:
*   **Task 1**: `python Task1_Chatbot/test_chatbot.py`
*   **Task 2**: `python Task2_TicTacToe/test_game.py`
*   **Task 3**: `python Task3_ImageCaptioning/test_caption.py`
*   **Task 4**: `python Task4_RecommendationSystem/test_recommend.py`
*   **Task 5**: `python Task5_FaceDetection/test_face.py`
