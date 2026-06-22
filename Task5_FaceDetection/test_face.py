import unittest
import base64
import os
import shutil
import numpy as np
import cv2
from face_engine import FaceEngine

class TestFaceEngine(unittest.TestCase):
    def setUp(self):
        # Create a mock face image: 100x100 solid gray square
        self.mock_face_img = np.ones((100, 100), dtype=np.uint8) * 128
        _, buffer = cv2.imencode('.png', self.mock_face_img)
        self.mock_face_b64 = "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')
        
        # Instantiate FaceEngine
        self.engine = FaceEngine()

    def test_registration_and_recognition(self):
        # Register the mock face
        name = "TestPerson"
        self.engine.register_face(name, self.mock_face_b64)
        
        # Check if the face is in the registry
        self.assertIn(name, self.engine.registered_faces)
        
        # Check if file was written to database folder
        filepath = os.path.join(self.engine.db_dir, f"{name}.png")
        self.assertTrue(os.path.exists(filepath))
        
        # Run recognition test
        matched_name, confidence = self.engine._recognize_face_vector(self.mock_face_img)
        
        # Recognition should be successful, naming it 'TestPerson' with near-perfect similarity
        self.assertEqual(matched_name, name)
        self.assertGreater(confidence, 0.95)

        # Cleanup created files
        if os.path.exists(filepath):
            os.remove(filepath)
        if name in self.engine.registered_faces:
            del self.engine.registered_faces[name]

if __name__ == "__main__":
    unittest.main()
