import unittest
from recommend import RecommendationEngine

class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RecommendationEngine()

    def test_content_filtering(self):
        # Query 'Inception' (m1) content similarities
        recs, explanation = self.engine.get_content_recommendations("m1", limit=3)
        
        self.assertEqual(len(recs), 3)
        self.assertEqual(explanation["target"]["title"], "Inception")
        
        # Verify cosine similarity is sorted in descending order
        scores = [r["score"] for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Check that similarity scores are bounded [0, 1]
        for score in scores:
            self.assertTrue(0 <= score <= 1.0)

    def test_collaborative_filtering(self):
        # Query recommendations for user 'Alice'
        recs, explanation = self.engine.get_collaborative_recommendations("Alice", limit=3)
        
        # Alice has rated some movies, so she should get some predictions for unrated ones
        self.assertTrue(len(recs) <= 3)
        
        # Verify predicted ratings are between 1 and 5
        for rec in recs:
            self.assertTrue(1.0 <= rec["predicted_rating"] <= 5.0)
            
        # Pearson similarity with Bob should be calculable
        self.assertIn("Bob", explanation["similarities"])
        bob_sim = explanation["similarities"]["Bob"]
        self.assertTrue(-1.0 <= bob_sim <= 1.0)

if __name__ == "__main__":
    unittest.main()
