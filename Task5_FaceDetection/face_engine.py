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

    def _load_persisted_faces(self):
        """Loads registered faces from the local faces_db folder."""
        for filename in os.listdir(self.db_dir):
            if filename.endswith('.png'):
                name = os.path.splitext(filename)[0]
                filepath = os.path.join(self.db_dir, filename)
                img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    resized = cv2.resize(img, (100, 100))
                    # Normalize vector
                    vector = resized.flatten().astype(np.float32) / 255.0
                    self.registered_faces[name] = vector

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
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
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
        vector = resized.flatten().astype(np.float32) / 255.0
        self.registered_faces[name] = vector
        return True

    def _recognize_face_vector(self, face_img):
        """
        Compares a detected face image against all registered profiles.
        Returns (name, confidence_score)
        """
        if not self.registered_faces:
            return "Unknown", 0.0

        # Preprocess input face
        resized = cv2.resize(face_img, (100, 100))
        input_vector = resized.flatten().astype(np.float32) / 255.0

        # L2 normalize input
        norm_input = np.linalg.norm(input_vector)
        if norm_input == 0:
            return "Unknown", 0.0
        input_vector = input_vector / norm_input

        best_score = -1.0
        best_name = "Unknown"

        for name, registered_vector in self.registered_faces.items():
            # L2 normalize registered vector
            norm_reg = np.linalg.norm(registered_vector)
            if norm_reg == 0:
                continue
            reg_vector = registered_vector / norm_reg

            # Calculate cosine similarity (dot product of normalized vectors)
            similarity = np.dot(input_vector, reg_vector)
            
            # Map cosine similarity [-1, 1] to a confidence value [0, 1]
            confidence = (similarity + 1.0) / 2.0
            
            if confidence > best_score:
                best_score = confidence
                best_name = name

        # Decision threshold (e.g. 80% confidence mapping)
        if best_score > 0.85:
            return best_name, float(best_score)
        
        return "Unknown", float(best_score)
