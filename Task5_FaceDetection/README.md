# Task 5: Face Detection & Recognition Profile Manager

A facial scanner application using OpenCV Haar cascades for detection and Cosine Similarity pixel descriptor comparisons for face recognition.

---

## 🚀 Key Features

*   **📷 Live HTML5 Webcam Streaming**: Grabs browser webcam frames every 500ms and sends them to the Python backend.
*   **👤 Haar Cascade Detection**: Detects faces in real time and draws bounding box coordinates and identifiers.
*   **👁️ Cosine Similarity Recognition**: Crops detected faces, normalizes contrast, resizes to a flat 100x100 array, and runs vector distance checks against registered templates.
*   **💾 Database Registration Modal**: Crop and save unknown face frames, enter profile names, and store them locally in `faces_db/` to immediately activate recognition matching.

---

## 🛠️ Requirements & Setup

Requires OpenCV and NumPy:
```powershell
pip install -r requirements.txt
```

---

## 📦 How to Run

1.  Navigate to the project directory:
    ```powershell
    cd Task5_FaceDetection
    ```
2.  **Start in Web Mode** (launches local server and opens browser):
    ```powershell
    python main.py
    ```
3.  **Start in Console Mode** (analyzes local file paths and saves `detected_*.jpeg` frames):
    ```powershell
    python main.py --console
    ```

---

## 🧪 Testing

Run unit tests checking profile registration and similarity coefficients:
```powershell
python test_face.py
```
