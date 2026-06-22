# Task 4: Content & Collaborative Recommendation Engine

A movie and book recommendation dashboard demonstrating Content-Based and User-Based Collaborative Filtering algorithms from scratch.

---

## 🚀 Key Features

*   **🎬 Content-Based Filtering**: Recommends items similar to a query item. Tokenizes descriptors, builds TF-IDF term weights, and computes Cosine Similarity vectors.
*   **👥 User-Based Collaborative Filtering**: Predicts ratings for unrated items by calculating Pearson Correlation coefficients among different user profiles.
*   **📐 Math Explanation Panels**:
    *   **Content mode**: Renders word weight overlaps and product calculations in a table.
    *   **Collaborative mode**: Visualizes user-to-user similarity cards.
*   **✍️ Dynamic Ratings Slider**: Adjust any user's rated list on the fly and watch predicted recommendations instantly shift.

---

## 📦 How to Run

1.  Navigate to the project directory:
    ```powershell
    cd Task4_RecommendationSystem
    ```
2.  **Start in Web Mode** (launches local server and opens browser):
    ```powershell
    python main.py
    ```
3.  **Start in Console Mode** (runs inside terminal):
    ```powershell
    python main.py --console
    ```

---

## 🧪 Testing

Run unit tests verifying content TF-IDF bounds and Pearson predictions:
```powershell
python test_recommend.py
```
