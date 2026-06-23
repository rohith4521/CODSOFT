import unittest
import base64
from caption_engine import CaptionEngine

class TestCaptionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CaptionEngine()
        # 1x1 black pixel base64 GIF
        self.test_b64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

    def test_lstm_trace(self):
        caption = "a brown dog running"
        trace = self.engine.simulate_lstm_trace(caption)
        
        # 'a brown dog running' is 4 words, so trace should have 5 steps (including <end> token)
        self.assertEqual(len(trace), 5)
        
        # Assert start context
        self.assertEqual(trace[0]['context'], "<start>")
        self.assertEqual(trace[0]['selected'], "a")
        
        # Check step numbers
        for i, step in enumerate(trace):
            self.assertEqual(step['step'], i + 1)
            # Ensure probabilities sum to 1.0 approximately
            total_prob = sum(cand['prob'] for cand in step['predictions'])
            self.assertAlmostEqual(total_prob, 1.0, places=1)

    def test_feature_maps(self):
        maps = self.engine.generate_feature_maps(self.test_b64)
        
        # Verify keys are present
        self.assertIn("layer1_edges", maps)
        self.assertIn("layer2_textures", maps)
        self.assertIn("layer3_parts", maps)
        self.assertIn("layer4_heatmap", maps)

    def test_heuristic_captioning(self):
        import numpy as np
        # Simulate a predominantly green BGR image (grass)
        green_img = np.zeros((224, 224, 3), dtype=np.uint8)
        green_img[:, :, 1] = 200 # Green channel high
        
        # BLIP-Base on dog image / grass should return "a dog sitting on the grass"
        blip_caption = self.engine.generate_heuristic_caption(green_img, "my_dog.jpg", "blip-base")
        self.assertEqual(blip_caption, "a dog sitting on the grass")

        # ViT-GPT2 on dog image / grass should return "a brown dog sitting on the green grass"
        vit_caption = self.engine.generate_heuristic_caption(green_img, "my_dog.jpg", "vit-gpt2")
        self.assertEqual(vit_caption, "a brown dog sitting on the green grass")

        # Generic dark image without keywords
        dark_img = np.zeros((224, 224, 3), dtype=np.uint8)
        blip_generic = self.engine.generate_heuristic_caption(dark_img, "image.png", "blip-base")
        self.assertNotEqual(blip_generic, "A subject situated on a green grassy field")
        self.assertIn("scene", blip_generic)

if __name__ == "__main__":
    unittest.main()
