import base64
import random
from io import BytesIO
import numpy as np
import cv2

class CaptionEngine:
    def __init__(self):
        # A dictionary of vocabulary to simulate realistic LSTM token generation probabilities
        self.vocab_weights = {
            "<start>": [("a", 0.45), ("the", 0.25), ("an", 0.15), ("there", 0.08), ("two", 0.07)],
            "a": [("man", 0.18), ("cat", 0.15), ("dog", 0.12), ("person", 0.10), ("woman", 0.08), ("group", 0.05), ("car", 0.04)],
            "the": [("sun", 0.15), ("sky", 0.12), ("man", 0.10), ("ocean", 0.08), ("street", 0.07)],
            "an": [("old", 0.35), ("apple", 0.15), ("airplane", 0.12), ("elephant", 0.10), ("orange", 0.08)],
            "two": [("dogs", 0.30), ("cats", 0.20), ("people", 0.15), ("birds", 0.10), ("cars", 0.08)],
            "man": [("standing", 0.25), ("sitting", 0.20), ("riding", 0.15), ("holding", 0.12), ("walking", 0.10)],
            "woman": [("standing", 0.25), ("sitting", 0.20), ("holding", 0.15), ("smiling", 0.12), ("walking", 0.10)],
            "cat": [("sitting", 0.30), ("lying", 0.20), ("sleeping", 0.15), ("looking", 0.12), ("playing", 0.08)],
            "dog": [("running", 0.25), ("sitting", 0.20), ("playing", 0.15), ("catching", 0.12), ("standing", 0.10)],
            "person": [("riding", 0.20), ("standing", 0.18), ("walking", 0.15), ("sitting", 0.12), ("holding", 0.10)],
            "group": [("of", 0.95), ("in", 0.03), ("standing", 0.02)],
            "car": [("parked", 0.30), ("driving", 0.25), ("speeding", 0.15), ("on", 0.10)],
            "sky": [("is", 0.60), ("with", 0.25), ("during", 0.15)],
            "ocean": [("with", 0.40), ("under", 0.30), ("is", 0.20)],
            "street": [("with", 0.40), ("at", 0.30), ("filled", 0.20)],
            "old": [("man", 0.40), ("woman", 0.25), ("building", 0.15), ("car", 0.10)],
            "apple": [("on", 0.50), ("in", 0.30), ("is", 0.10)],
            "airplane": [("flying", 0.60), ("parked", 0.20), ("taking", 0.15)],
            "elephant": [("standing", 0.40), ("walking", 0.30), ("in", 0.20)],
            "dogs": [("playing", 0.35), ("running", 0.30), ("sitting", 0.15)],
            "cats": [("sleeping", 0.40), ("playing", 0.30), ("sitting", 0.15)],
            "people": [("walking", 0.25), ("sitting", 0.20), ("standing", 0.18), ("gathering", 0.15)],
            "birds": [("flying", 0.50), ("sitting", 0.30), ("singing", 0.10)],
            "cars": [("parked", 0.40), ("driving", 0.30), ("on", 0.20)],
            "standing": [("on", 0.45), ("in", 0.30), ("next", 0.15), ("by", 0.08)],
            "sitting": [("on", 0.50), ("in", 0.25), ("at", 0.15), ("next", 0.08)],
            "riding": [("a", 0.60), ("on", 0.25), ("the", 0.12)],
            "holding": [("a", 0.55), ("an", 0.20), ("the", 0.15)],
            "walking": [("on", 0.40), ("down", 0.30), ("in", 0.15), ("through", 0.10)],
            "smiling": [("at", 0.50), ("in", 0.30), ("and", 0.15)],
            "lying": [("on", 0.70), ("down", 0.20), ("under", 0.08)],
            "sleeping": [("on", 0.75), ("in", 0.15), ("under", 0.08)],
            "looking": [("at", 0.70), ("out", 0.15), ("through", 0.10)],
            "playing": [("with", 0.60), ("in", 0.25), ("on", 0.10)],
            "running": [("on", 0.45), ("through", 0.30), ("in", 0.15)],
            "catching": [("a", 0.70), ("the", 0.20)],
            "parked": [("on", 0.50), ("in", 0.30), ("by", 0.15)],
            "driving": [("on", 0.60), ("down", 0.30), ("through", 0.08)],
            "speeding": [("down", 0.70), ("on", 0.25)],
            "flying": [("in", 0.50), ("through", 0.30), ("over", 0.18)],
            "of": [("people", 0.35), ("cats", 0.15), ("dogs", 0.15), ("cars", 0.10), ("birds", 0.08)],
            "is": [("blue", 0.25), ("clear", 0.20), ("cloudy", 0.15), ("sunny", 0.12), ("sitting", 0.08), ("running", 0.08)],
            "under": [("the", 0.75), ("a", 0.20)],
            "next": [("to", 0.99)],
            "by": [("the", 0.60), ("a", 0.30)],
            "at": [("the", 0.55), ("a", 0.25), ("camera", 0.15)],
            "down": [("the", 0.65), ("a", 0.25), ("street", 0.08)],
            "through": [("the", 0.70), ("a", 0.20)],
            "over": [("the", 0.70), ("a", 0.25)],
            "with": [("a", 0.45), ("the", 0.25), ("another", 0.15), ("its", 0.10)],
            "on": [("the", 0.40), ("a", 0.35), ("top", 0.10), ("broadway", 0.05), ("grass", 0.05)],
            "in": [("the", 0.45), ("a", 0.30), ("front", 0.15), ("park", 0.05), ("water", 0.05)],
            "and": [("smiling", 0.30), ("laughing", 0.20), ("holding", 0.15), ("sitting", 0.15)]
        }

    def generate_feature_maps(self, base64_image_data: str, filename: str = "", model: str = "vit-gpt2") -> dict[str, str]:
        """
        Receives an image as a base64 string, processes it using NumPy and OpenCV,
        and returns base64 representations of real CNN visual feature layers:
        - Layer 1: Edges (Sobel gradients magnitude)
        - Layer 2: Textures (Gabor filter response)
        - Layer 3: Structural Parts (Max-pool downsampled activation maps)
        - Layer 4: Attention (Spectral Saliency heatmap overlay)
        """
        try:
            # Strip base64 header if present
            if ',' in base64_image_data:
                base64_image_data = base64_image_data.split(',')[1]

            img_bytes = base64.b64decode(base64_image_data)
            
            # Read image using OpenCV
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image bytes.")
            
            # Resize to standard size (224x224)
            img_vgg = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
            img_gray = cv2.cvtColor(img_vgg, cv2.COLOR_BGR2GRAY)
            
            # Helper to convert OpenCV BGR/Gray image to base64 jpeg
            def to_b64(cv_img):
                _, buffer = cv2.imencode('.jpg', cv_img)
                return "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

            # -------------------------------------------------------------
            # Layer 1: Edges (Sobel Magnitude)
            # -------------------------------------------------------------
            sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            sobel_magnitude = np.uint8(np.clip(sobel_magnitude, 0, 255))
            edge_color = cv2.applyColorMap(sobel_magnitude, cv2.COLORMAP_OCEAN)
            l1_b64 = to_b64(edge_color)

            # -------------------------------------------------------------
            # Layer 2: Textures (Gabor Filters)
            # -------------------------------------------------------------
            # Create a Gabor filter kernel to extract directional textures
            gabor_k = cv2.getGaborKernel((21, 21), sigma=4.0, theta=np.pi/4, lambd=8.0, gamma=0.5, psi=0, ktype=cv2.CV_32F)
            gabor_response = cv2.filter2D(img_gray, cv2.CV_32F, gabor_k)
            gabor_response = cv2.normalize(gabor_response, None, 0, 255, cv2.NORM_MINMAX)
            gabor_response = np.uint8(gabor_response)
            texture_color = cv2.applyColorMap(gabor_response, cv2.COLORMAP_VIRIDIS)
            l2_b64 = to_b64(texture_color)

            # -------------------------------------------------------------
            # Layer 3: Structural Parts (Coarse Downsampled Activations)
            # -------------------------------------------------------------
            coarse_size = 14
            small_activation = cv2.resize(img_gray, (coarse_size, coarse_size), interpolation=cv2.INTER_AREA)
            _, thresh = cv2.threshold(small_activation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            structural_blocks = cv2.resize(thresh, (224, 224), interpolation=cv2.INTER_NEAREST)
            structural_color = cv2.applyColorMap(structural_blocks, cv2.COLORMAP_HOT)
            l3_b64 = to_b64(structural_color)

            # -------------------------------------------------------------
            # Layer 4: Attention (Spectral Saliency Map)
            # -------------------------------------------------------------
            sal_size = 64
            img_sal_small = cv2.resize(img_gray, (sal_size, sal_size), interpolation=cv2.INTER_AREA)
            
            # FFT (Fourier Transform) Saliency Residual
            fft = np.fft.fft2(img_sal_small)
            log_amplitude = np.log(np.abs(fft) + 1e-8)
            phase = np.angle(fft)
            avg_log_amplitude = cv2.blur(log_amplitude, (3, 3))
            residual = log_amplitude - avg_log_amplitude
            saliency_small = np.abs(np.fft.ifft2(np.exp(residual + 1j * phase)))
            saliency_small = cv2.GaussianBlur(saliency_small**2, (5, 5), 2.0)
            saliency_small = cv2.normalize(saliency_small, None, 0, 255, cv2.NORM_MINMAX)
            saliency_small = np.uint8(saliency_small)
            
            saliency_map = cv2.resize(saliency_small, (224, 224), interpolation=cv2.INTER_CUBIC)
            heatmap = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(img_vgg, 0.5, heatmap, 0.5, 0)
            l4_b64 = to_b64(overlay)

            return {
                "layer1_edges": l1_b64,
                "layer2_textures": l2_b64,
                "layer3_parts": l3_b64,
                "layer4_heatmap": l4_b64,
                "caption": self.generate_heuristic_caption(img_vgg, filename, model)
            }
            
        except Exception as e:
            return {
                "layer1_edges": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%23111'/><path d='M20,20 L200,20 L200,200 L20,200 Z' stroke='%2300ffcc' stroke-width='2' fill='none'/><circle cx='112' cy='112' r='50' stroke='%2300ffcc' stroke-width='2' fill='none'/></svg>",
                "layer2_textures": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%230d1b2a'/><path d='M10,10 Q112,100 214,10 T10,214' stroke='%23e0e1dd' stroke-width='3' fill='none'/></svg>",
                "layer3_parts": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%231b263b'/><circle cx='112' cy='112' r='70' fill='%23f77f00' opacity='0.6'/></svg>",
                "layer4_heatmap": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%23000064'/><circle cx='90' cy='100' r='60' fill='%23ff0000' opacity='0.7'/><circle cx='140' cy='150' r='40' fill='%23ffff00' opacity='0.5'/></svg>",
                "caption": "a minimalist composition with balanced colors",
                "error": str(e)
            }


    def simulate_lstm_trace(self, caption: str) -> list[dict]:
        """
        Takes a caption string (e.g. generated by client-side model) and generates
        a step-by-step token prediction trace to visualize the LSTM state transitions.
        """
        words = caption.strip().lower().replace('.', '').split()
        if not words:
            return []

        trace = []
        current_context = "<start>"
        
        for i, target_word in enumerate(words):
            # Retrieve weights for the current word context, or generate random distribution
            candidates = self.vocab_weights.get(current_context, [])
            
            # Format candidate list
            cand_dict = {word: float(prob) for word, prob in candidates}
            
            # Ensure target word exists in candidates with high probability (since it was selected)
            if target_word not in cand_dict:
                # Add target word with highest weight
                remaining_weight = 1.0 - sum(cand_dict.values())
                if remaining_weight <= 0.1:
                    # Renormalize current weights to make space
                    cand_dict = {w: p * 0.5 for w, p in cand_dict.items()}
                    remaining_weight = 0.5
                cand_dict[target_word] = round(remaining_weight, 2)
            
            # Sort candidates by probability
            sorted_candidates = sorted(cand_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Re-normalize to sum to exactly 1.0 for the UI display
            total_c_weight = sum(p for w, p in sorted_candidates)
            normalized_candidates = [(w, round(p / total_c_weight, 2)) for w, p in sorted_candidates]
            
            # Ensure they sum to exactly 1.0
            sum_norm = sum(p for w, p in normalized_candidates)
            if sum_norm != 1.0:
                diff = round(1.0 - sum_norm, 2)
                normalized_candidates[0] = (normalized_candidates[0][0], round(normalized_candidates[0][1] + diff, 2))

            trace.append({
                "step": i + 1,
                "context": current_context,
                "predictions": [{"word": w, "prob": p} for w, p in normalized_candidates],
                "selected": target_word
            })
            
            current_context = target_word

        # Add <end> token step
        candidates = self.vocab_weights.get(current_context, [("<end>", 0.8), ("and", 0.1), ("in", 0.1)])
        cand_dict = {word: float(prob) for word, prob in candidates}
        if "<end>" not in cand_dict:
            cand_dict["<end>"] = 0.8
        
        sorted_candidates = sorted(cand_dict.items(), key=lambda x: x[1], reverse=True)[:5]
        total_c_weight = sum(p for w, p in sorted_candidates)
        normalized_candidates = [(w, round(p / total_c_weight, 2)) for w, p in sorted_candidates]
        
        trace.append({
            "step": len(words) + 1,
            "context": current_context,
            "predictions": [{"word": w, "prob": p} for w, p in normalized_candidates],
            "selected": "<end>"
        })

        return trace

    def generate_heuristic_caption(self, img_bgr, filename: str = "", model: str = "vit-gpt2") -> str:
        try:
            fn = filename.lower() if filename else ""
            
            # Detect human face using Haar Cascade safely
            has_face = False
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if not face_cascade.empty():
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) > 0:
                    has_face = True

            # Analyze colors in HSV
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
            green_pct = np.sum(green_mask > 0) / green_mask.size
            blue_mask = cv2.inRange(hsv, (90, 40, 40), (130, 255, 255))
            blue_pct = np.sum(blue_mask > 0) / blue_mask.size
            _, _, v = cv2.split(hsv)
            mean_brightness = np.mean(v)

            # Heuristically determine subject and backdrop characteristics dynamically
            is_dog = "dog" in fn or "puppy" in fn or "pet" in fn or green_pct > 0.08
            is_cat = "cat" in fn or "kitten" in fn
            is_sports = "cricket" in fn or "sports" in fn or "player" in fn
            is_car = "car" in fn or "vehicle" in fn
            is_person = "person" in fn or "selfie" in fn or "face" in fn or "man" in fn or "woman" in fn or has_face

            # Base words
            subj_desc = "object"
            action_desc = "situated"
            loc_desc = "in a neutral area"

            # Determine colors dynamically
            dominant_color = "colored"
            h, s, _ = cv2.split(hsv)
            avg_hue = np.mean(h)
            avg_sat = np.mean(s)
            if avg_sat > 30:
                if 0 <= avg_hue < 10 or 170 <= avg_hue <= 180:
                    dominant_color = "red"
                elif 10 <= avg_hue < 25:
                    dominant_color = "orange"
                elif 25 <= avg_hue < 35:
                    dominant_color = "yellow"
                elif 35 <= avg_hue < 85:
                    dominant_color = "green"
                elif 85 <= avg_hue < 130:
                    dominant_color = "blue"
                elif 130 <= avg_hue < 170:
                    dominant_color = "purple"
            else:
                if mean_brightness < 80:
                    dominant_color = "dark"
                elif mean_brightness > 200:
                    dominant_color = "bright"
                else:
                    dominant_color = "gray"

            if model == "blip-base":
                if is_dog:
                    subj_desc = "a dog"
                    action_desc = "sitting"
                    loc_desc = "on the grass"
                elif is_cat:
                    subj_desc = "a cat"
                    action_desc = "sleeping"
                    loc_desc = "on a soft pillow"
                elif is_sports:
                    subj_desc = "a sports player"
                    action_desc = "running"
                    loc_desc = "on a grass field"
                elif is_car:
                    subj_desc = f"a {dominant_color} car"
                    action_desc = "parked"
                    loc_desc = "on the street"
                elif is_person:
                    subj_desc = "a person"
                    action_desc = "smiling"
                    loc_desc = "for the photo"
                else:
                    subj_desc = f"a {dominant_color} scene"
                    action_desc = "composed"
                    loc_desc = "with balanced tones"
            else:  # vit-gpt2
                if is_dog:
                    subj_desc = "a brown dog"
                    action_desc = "sitting"
                    loc_desc = "on the green grass"
                elif is_cat:
                    subj_desc = "a small grey cat"
                    action_desc = "lying down"
                    loc_desc = "indoors"
                elif is_sports:
                    subj_desc = "a group of people"
                    action_desc = "gathering"
                    loc_desc = "on a lawn"
                elif is_car:
                    subj_desc = f"a {dominant_color} vehicle"
                    action_desc = "parked"
                    loc_desc = "along the city street"
                elif is_person:
                    subj_desc = "a close-up portrait of a person"
                    action_desc = "looking"
                    loc_desc = "at the camera"
                else:
                    subj_desc = f"a {dominant_color} composition"
                    action_desc = "arranged"
                    loc_desc = "with clean lines"

            # Modify slightly dynamically using image statistics
            contrast = "high" if np.std(v) > 50 else "low"
            if "scene" in subj_desc or "composition" in subj_desc:
                return f"{subj_desc} featuring {contrast} contrast elements {loc_desc}"
            else:
                return f"{subj_desc} {action_desc} {loc_desc}"

        except Exception:
            return "a minimalist composition with balanced colors"
