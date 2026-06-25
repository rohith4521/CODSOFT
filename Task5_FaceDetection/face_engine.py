import cv2
import numpy as np
import base64
import os

class FaceEngine:
    def __init__(self):
        # Path to Haar cascade XML
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise IOError("Failed to load Haar Cascade face detector.")

        # Database of registered faces
        # Key: username, Value: 100x100 normalized flat pixel vector
        self.registered_faces = {}
        
        # Directory to persist registered faces locally
        self.db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faces_db')
        os.makedirs(self.db_dir, exist_ok=True)
        self._load_persisted_faces()

    def _preprocess_face(self, face_img):
        """Resizes, equalizes histogram, subtracts mean, and normalizes vector."""
        resized = cv2.resize(face_img, (100, 100))
        
        # Inner 80% crop to ignore hair, ears, beard contours, and background
        inner = resized[10:90, 10:90]
        resized = cv2.resize(inner, (100, 100))
        
        equalized = cv2.equalizeHist(resized)
        vector = equalized.flatten().astype(np.float32)
        
        # Center the vector (Pearson Correlation centering)
        mean = np.mean(vector)
        vector = vector - mean
        
        # L2 Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def _load_persisted_faces(self):
        """Loads registered faces from the local faces_db folder."""
        for filename in os.listdir(self.db_dir):
            if filename.endswith('.png'):
                name = os.path.splitext(filename)[0]
                filepath = os.path.join(self.db_dir, filename)
                img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.registered_faces[name] = self._preprocess_face(img)

    def detect_faces(self, image_bytes):
        """
        Detects faces in raw image bytes.
        Returns:
            - list of dicts: [{"x", "y", "w", "h", "cropped_b64"}]
            - frame_b64: base64 string of image with bounding boxes drawn
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image format.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with parameters optimized for better recall
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=4,
            minSize=(30, 30)
        )

        detected_list = []
        img_out = img.copy()

        for (x, y, w, h) in faces:
            # Crop face
            face_crop = gray[y:y+h, x:x+w]
            resized_crop = cv2.resize(face_crop, (100, 100))
            
            # Encode cropped face to base64
            _, buffer = cv2.imencode('.png', resized_crop)
            crop_b64 = "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')

            # Identify if it matches any registered face
            name, confidence = self._recognize_face_vector(resized_crop)

            detected_list.append({
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "crop_b64": crop_b64,
                "name": name,
                "confidence": confidence
            })

            # Draw rectangle and name label
            color = (0, 245, 212) if name != "Unknown" else (0, 114, 255) # neon green if known, blue if unknown
            cv2.rectangle(img_out, (x, y), (x+w, y+h), color, 2)
            
            label = f"{name} ({int(confidence*100)}%)" if name != "Unknown" else "Unknown Face"
            cv2.putText(img_out, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Encode resulting image
        _, buffer_out = cv2.imencode('.jpeg', img_out)
        frame_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer_out).decode('utf-8')

        return detected_list, frame_b64

    def register_face(self, name, crop_b64):
        """
        Registers a new face.
        `crop_b64` is a base64 string of the cropped face image.
        """
        # Strip header
        if ',' in crop_b64:
            crop_b64 = crop_b64.split(',')[1]
            
        crop_bytes = base64.b64decode(crop_b64)
        nparr = np.frombuffer(crop_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError("Failed to decode cropped face image.")

        # Resize to standard size
        resized = cv2.resize(img, (100, 100))
        
        # Save to persist directory
        filepath = os.path.join(self.db_dir, f"{name}.png")
        cv2.imwrite(filepath, resized)

        # Update runtime database
        self.registered_faces[name] = self._preprocess_face(resized)
        return True

    def _recognize_face_vector(self, face_img):
        """
        Compares a detected face image against all registered profiles.
        Returns (name, confidence_score)
        """
        if not self.registered_faces:
            return "Unknown", 0.0

        # Search over a grid of small shifts (dx, dy) to compensate for Haar Cascade
        # bounding box alignment jitter and recover optimal correlation.
        best_score = -1.0
        best_name = "Unknown"
        
        h, w = face_img.shape[:2]
        shifted_vectors = []
        for dy in [-8, -4, 0, 4, 8]:
            for dx in [-8, -4, 0, 4, 8]:
                if dx == 0 and dy == 0:
                    realigned = face_img
                else:
                    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
                    realigned = cv2.warpAffine(face_img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
                
                v_realigned = self._preprocess_face(realigned)
                shifted_vectors.append(v_realigned)

        for name, reg_vector in self.registered_faces.items():
            for v_input in shifted_vectors:
                similarity = np.dot(v_input, reg_vector)
                confidence = (similarity + 1.0) / 2.0
                
                if confidence > best_score:
                    best_score = confidence
                    best_name = name

        # Tightened decision threshold (82% confidence mapping, equivalent to 0.64 correlation)
        # to prevent similar family members or siblings from false-matching.
        if best_score > 0.82:
            return best_name, float(best_score)
        
        return "Unknown", float(best_score)
