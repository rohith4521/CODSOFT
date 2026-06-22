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

if __name__ == "__main__":
    unittest.main()
