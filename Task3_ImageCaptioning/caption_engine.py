import base64
import random
from io import BytesIO

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

    def generate_feature_maps(self, base64_image_data: str) -> dict[str, str]:
        """
        Receives an image as a base64 string, processes it in pure Python,
        and returns base64 representations of VGG/ResNet simulated feature layers.
        """
        try:
            # Strip base64 header if present
            if ',' in base64_image_data:
                base64_image_data = base64_image_data.split(',')[1]

            img_bytes = base64.b64decode(base64_image_data)
            
            # Use basic PPM/PGM manipulation or simple raw image reading to extract pixels
            # To be 100% robust without PIL or cv2, we parse the JPEG/PNG using standard library
            # Or we can import PIL if the user installs it. Since we want no-fail, we'll try to use PIL (Pillow)
            # if installed, or fallback to returning stylized SVG/Canvas-based data or procedurally generated map streams.
            # Let's try importing PIL. If PIL is not available, we can mock visual feature maps using procedural patterns
            # combined with the original image, or we can use simple resizing if PIL is imported.
            try:
                from PIL import Image, ImageFilter, ImageOps
                img = Image.open(BytesIO(img_bytes))
                
                # Resize to standard size for VGG (224x224)
                img_vgg = img.resize((224, 224))
                
                # Generate 4 layers of feature maps
                # Layer 1: Edges (High pass filter / Sobel equivalent)
                l1 = img_vgg.convert('L').filter(ImageFilter.FIND_EDGES)
                
                # Layer 2: Textures (Gradients + Color accents)
                l2 = img_vgg.filter(ImageFilter.SHARPEN)
                l2 = ImageOps.colorize(l2.convert('L'), '#0d1b2a', '#e0e1dd')
                
                # Layer 3: Structural Parts (High contrast threshold + Blur)
                l3 = img_vgg.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
                l3 = l3.convert('L').filter(ImageFilter.GaussianBlur(radius=2))
                l3 = ImageOps.colorize(l3, '#1b263b', '#f77f00')
                
                # Layer 4: High-level Activation Heatmap (Class activation map)
                # Let's draw a radial gradient overlay on the image to simulate attention heatmaps
                w, h = img_vgg.size
                heatmap = Image.new('RGB', (w, h), color=(0, 0, 100))
                # Add hot spots
                from PIL import ImageDraw
                draw = ImageDraw.Draw(heatmap)
                for _ in range(3):
                    cx, cy = random.randint(50, 170), random.randint(50, 170)
                    r = random.randint(40, 80)
                    for r_i in range(r, 0, -5):
                        intensity = int(255 * (1 - r_i / r))
                        draw.ellipse([cx - r_i, cy - r_i, cx + r_i, cy + r_i], fill=(intensity, 0, 100 - int(intensity/3)))
                
                l4 = Image.blend(img_vgg, heatmap, 0.5)
                
                # Helper to convert PIL Image to base64
                def to_b64(pil_img):
                    buffer = BytesIO()
                    pil_img.save(buffer, format="JPEG")
                    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return {
                    "layer1_edges": to_b64(l1),
                    "layer2_textures": to_b64(l2),
                    "layer3_parts": to_b64(l3),
                    "layer4_heatmap": to_b64(l4)
                }
            except ImportError:
                # Fallback: if PIL is not installed, we can generate simulated SVG data URLs or returns placeholder base64 maps
                # We will recommend PIL in instructions, but we provide elegant procedural fallback so it NEVER throws a 500 error.
                return {
                    "layer1_edges": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%23111'/><path d='M20,20 L200,20 L200,200 L20,200 Z' stroke='%2300ffcc' stroke-width='2' fill='none'/><circle cx='112' cy='112' r='50' stroke='%2300ffcc' stroke-width='2' fill='none'/></svg>",
                    "layer2_textures": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%230d1b2a'/><path d='M10,10 Q112,100 214,10 T10,214' stroke='%23e0e1dd' stroke-width='3' fill='none'/></svg>",
                    "layer3_parts": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%231b263b'/><circle cx='112' cy='112' r='70' fill='%23f77f00' opacity='0.6'/></svg>",
                    "layer4_heatmap": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%23000064'/><circle cx='90' cy='100' r='60' fill='%23ff0000' opacity='0.7'/><circle cx='140' cy='150' r='40' fill='%23ffff00' opacity='0.5'/></svg>"
                }
        except Exception as e:
            return {"error": str(e)}

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
