import math
import re

class RecommendationEngine:
    def __init__(self):
        # Database of items (Movies & Books)
        self.movies = [
            {"id": "m1", "title": "Inception", "genre": "Sci-Fi Thriller Action", "desc": "A thief steals corporate secrets through dream-sharing technology."},
            {"id": "m2", "title": "Interstellar", "genre": "Sci-Fi Adventure Drama", "desc": "A team of explorers travel through a wormhole in space to save humanity."},
            {"id": "m3", "title": "The Dark Knight", "genre": "Action Crime Drama Thriller", "desc": "Batman faces the Joker in a psychological battle of chaos and justice."},
            {"id": "m4", "title": "Pulp Fiction", "genre": "Crime Drama", "desc": "The lives of mob hitmen, a boxer, and bandits intertwine in quirky stories."},
            {"id": "m5", "title": "The Matrix", "genre": "Sci-Fi Action Thriller", "desc": "A hacker discovers the world is a simulated reality run by machines."},
            {"id": "m6", "title": "Spirited Away", "genre": "Animation Fantasy Adventure Family", "desc": "A young girl wanders into a world ruled by gods, witches, and spirits."},
            {"id": "m7", "title": "The Godfather", "genre": "Crime Drama", "desc": "The aging patriarch of an organized crime dynasty transfers control to his son."},
            {"id": "m8", "title": "Avatar", "genre": "Sci-Fi Action Adventure Fantasy", "desc": "A paraplegic Marine dispatched to the moon Pandora becomes torn between worlds."},
            {"id": "m9", "title": "Gladiator", "genre": "Action Adventure Drama", "desc": "A former Roman General sets out to exact vengeance against the corrupt emperor."},
            {"id": "m10", "title": "Parasite", "genre": "Thriller Drama Comedy", "desc": "Greed and class discrimination threaten the relationship between two families."}
        ]

        self.books = [
            {"id": "b1", "title": "Dune", "genre": "Sci-Fi Fantasy Adventure", "desc": "A noble family becomes embroiled in a battle for control of a desert planet."},
            {"id": "b2", "title": "Neuromancer", "genre": "Sci-Fi Cyberpunk Thriller", "desc": "A washed-up computer hacker is hired for one last ultimate hack in cyberspace."},
            {"id": "b3", "title": "The Hobbit", "genre": "Fantasy Adventure", "desc": "A home-loving hobbit embarks on a quest to win a share of dragon-guarded treasure."},
            {"id": "b4", "title": "Sherlock Holmes", "genre": "Mystery Crime Detective", "desc": "A consulting detective solves complex mysteries in Victorian London."},
            {"id": "b5", "title": "The Great Gatsby", "genre": "Drama Romance Classic", "desc": "A writer becomes fascinated by his mysterious millionaire neighbor Jay Gatsby."},
            {"id": "b6", "title": "Foundation", "genre": "Sci-Fi Space-Opera Future", "desc": "A mathematician plans the preservation of knowledge as galactic empire crumbles."},
            {"id": "b7", "title": "Pride and Prejudice", "genre": "Classic Romance Comedy Drama", "desc": "Sparks fly when spirited Elizabeth Bennet meets single, rich Mr. Darcy."},
            {"id": "b8", "title": "Dracula", "genre": "Horror Thriller Classic Mystery", "desc": "Count Dracula attempts to move from Transylvania to England to find new blood."},
            {"id": "b9", "title": "The Lord of the Rings", "genre": "Fantasy Adventure Epic", "desc": "A fellowship seeks to destroy the One Ring to save Middle-earth from Sauron."},
            {"id": "b10", "title": "Gone Girl", "genre": "Mystery Thriller Suspense Crime", "desc": "A husband becomes the prime suspect when his wife mysteriously vanishes on their anniversary."}
        ]

        self.all_items = self.movies + self.books
        self.item_by_id = {item["id"]: item for item in self.all_items}

        # Simulated User-Item Ratings matrix for Collaborative Filtering
        # Rows: Users, Cols: Item IDs (Ratings 1-5, 0 represents unrated)
        self.users = {
            "Alice": {"m1": 5, "m2": 4, "m5": 5, "b1": 4, "b2": 5, "m3": 0, "m4": 0, "b3": 0, "b4": 3, "m6": 0},
            "Bob": {"m1": 4, "m2": 5, "m5": 0, "b1": 5, "b2": 4, "m3": 4, "m4": 0, "b3": 5, "b4": 0, "m6": 3},
            "Charlie": {"m1": 0, "m2": 0, "m5": 1, "b1": 2, "b2": 0, "m3": 5, "m4": 5, "b3": 4, "b4": 5, "m6": 0},
            "David": {"m1": 2, "m2": 1, "m5": 3, "b1": 0, "b2": 2, "m4": 4, "m7": 5, "b8": 4, "b10": 5, "m6": 0},
            "Emma": {"m1": 0, "m2": 4, "m5": 4, "b1": 3, "b6": 5, "m3": 3, "b3": 0, "b5": 4, "b7": 5, "m6": 4}
        }

    # Content-based Filtering Implementation (TF-IDF + Cosine Similarity)
    def _tokenize(self, text):
        return re.findall(r'\b[a-z]{3,15}\b', text.lower())

    def _compute_tfidf(self, items):
        # 1. Compute term frequencies (TF) and build vocabulary
        documents = []
        vocab = set()
        for item in items:
            text = f"{item['genre']} {item['desc']}"
            tokens = self._tokenize(text)
            doc_tf = {}
            for t in tokens:
                doc_tf[t] = doc_tf.get(t, 0) + 1
            documents.append((item['id'], doc_tf))
            vocab.update(doc_tf.keys())

        vocab = sorted(list(vocab))
        
        # 2. Compute inverse document frequency (IDF)
        n_docs = len(items)
        idf = {}
        for term in vocab:
            doc_count = sum(1 for _, doc_tf in documents if term in doc_tf)
            # Standard smooth idf formula
            idf[term] = math.log((1 + n_docs) / (1 + doc_count)) + 1

        # 3. Compute TF-IDF vectors
        tfidf_vectors = {}
        for item_id, doc_tf in documents:
            vector = {}
            for term, tf in doc_tf.items():
                vector[term] = tf * idf[term]
            
            # L2 Normalization
            length = math.sqrt(sum(val ** 2 for val in vector.values()))
            if length > 0:
                normalized_vector = {term: val / length for term, val in vector.items()}
            else:
                normalized_vector = {}
            tfidf_vectors[item_id] = normalized_vector

        return tfidf_vectors, idf

    def _cosine_similarity(self, vec1, vec2):
        dot_product = 0
        for term, val in vec1.items():
            if term in vec2:
                dot_product += val * vec2[term]
        return dot_product

    def get_content_recommendations(self, item_id, limit=5):
        """
        Calculates item similarity based on TF-IDF vectors of genre + description,
        and returns recommended items along with step-by-step math explanations.
        """
        # Determine subset (movies or books)
        target_item = self.item_by_id.get(item_id)
        if not target_item:
            return [], {}

        is_movie = item_id.startswith('m')
        subset = self.movies if is_movie else self.books

        tfidf_vectors, idf = self._compute_tfidf(subset)
        target_vector = tfidf_vectors[item_id]

        scores = []
        math_details = []

        for item in subset:
            if item["id"] == item_id:
                continue
            
            other_vector = tfidf_vectors[item["id"]]
            score = self._cosine_similarity(target_vector, other_vector)
            scores.append((item["id"], score))
            
            # Record math details for the step-by-step display
            overlapping_terms = []
            for term in target_vector:
                if term in other_vector:
                    overlapping_terms.append({
                        "term": term,
                        "v1_val": round(target_vector[term], 3),
                        "v2_val": round(other_vector[term], 3),
                        "product": round(target_vector[term] * other_vector[term], 3)
                    })
            
            math_details.append({
                "item_id": item["id"],
                "title": item["title"],
                "overlap": sorted(overlapping_terms, key=lambda x: x["product"], reverse=True)[:5],
                "score": round(score, 4)
            })

        # Sort recommendations
        scores.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = scores[:limit]

        recs_list = []
        for rec_id, score in top_recommendations:
            item = self.item_by_id[rec_id]
            recs_list.append({
                "id": item["id"],
                "title": item["title"],
                "genre": item["genre"],
                "desc": item["desc"],
                "score": round(score, 3)
            })

        explanation = {
            "target": target_item,
            "math": {det["item_id"]: det for det in math_details}
        }

        return recs_list, explanation

    # Collaborative Filtering Implementation (User-Based Correlation)
    def _user_mean_rating(self, ratings):
        rated_vals = [val for val in ratings.values() if val > 0]
        return sum(rated_vals) / len(rated_vals) if rated_vals else 0

    def _user_pearson_correlation(self, user1_ratings, user2_ratings):
        # Find common rated items
        common_items = [item for item in user1_ratings if user1_ratings[item] > 0 and user2_ratings.get(item, 0) > 0]
        if not common_items:
            return 0

        mean1 = self._user_mean_rating(user1_ratings)
        mean2 = self._user_mean_rating(user2_ratings)

        num = 0
        den1 = 0
        den2 = 0
        for item in common_items:
            diff1 = user1_ratings[item] - mean1
            diff2 = user2_ratings[item] - mean2
            num += diff1 * diff2
            den1 += diff1 ** 2
            den2 += diff2 ** 2

        if den1 == 0 or den2 == 0:
            return 0
            
        return num / math.sqrt(den1 * den2)

    def get_collaborative_recommendations(self, target_user, limit=5):
        """
        Uses User-Based Collaborative Filtering to recommend movies or books.
        """
        if target_user not in self.users:
            return [], {}

        user_ratings = self.users[target_user]
        user_mean = self._user_mean_rating(user_ratings)

        # Calculate Pearson similarities with all other users
        similarities = {}
        for other_user, other_ratings in self.users.items():
            if other_user == target_user:
                continue
            sim = self._user_pearson_correlation(user_ratings, other_ratings)
            similarities[other_user] = sim

        # Predict ratings for unrated items
        all_item_ids = set()
        for u in self.users.values():
            all_item_ids.update(u.keys())
        
        predictions = []
        math_details = []

        for item_id in all_item_ids:
            # Skip if user has already rated this item
            if user_ratings.get(item_id, 0) > 0:
                continue

            num = 0
            den = 0
            contributors = []
            
            for other_user, sim in similarities.items():
                other_rating = self.users[other_user].get(item_id, 0)
                if other_rating > 0 and sim > 0: # Only consider positively correlated neighbors
                    other_mean = self._user_mean_rating(self.users[other_user])
                    adjusted_rating = other_rating - other_mean
                    num += sim * adjusted_rating
                    den += abs(sim)
                    contributors.append({
                        "user": other_user,
                        "similarity": round(sim, 3),
                        "rating": other_rating,
                        "mean": round(other_mean, 2),
                        "adjusted": round(adjusted_rating, 2)
                    })

            if den > 0:
                predicted_rating = user_mean + (num / den)
                # Bound rating between 1 and 5
                predicted_rating = max(1.0, min(5.0, predicted_rating))
                predictions.append((item_id, predicted_rating))
                
                math_details.append({
                    "item_id": item_id,
                    "title": self.item_by_id[item_id]["title"],
                    "user_mean": round(user_mean, 2),
                    "contributors": contributors,
                    "predicted": round(predicted_rating, 3)
                })

        # Sort recommendations
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_recs = predictions[:limit]

        recs_list = []
        for rec_id, score in top_recs:
            item = self.item_by_id[rec_id]
            recs_list.append({
                "id": item["id"],
                "title": item["title"],
                "genre": item["genre"],
                "desc": item["desc"],
                "predicted_rating": round(score, 1)
            })

        explanation = {
            "similarities": {u: round(s, 3) for u, s in similarities.items()},
            "math": {det["item_id"]: det for det in math_details}
        }

        return recs_list, explanation
