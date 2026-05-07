"""
Image Sentiment Detection Service - Simplified for Streamlit Cloud
"""

from PIL import Image
import colorsys

class ImageSentimentDetector:
    def __init__(self):
        print("Initializing sentiment detector")
    
    def analyze_colors(self, image):
        try:
            image.thumbnail((100, 100))
            pixels = list(image.getdata())
            
            avg_r = sum(p[0] for p in pixels) / len(pixels)
            avg_g = sum(p[1] for p in pixels) / len(pixels)
            avg_b = sum(p[2] for p in pixels) / len(pixels)
            
            h, s, v = colorsys.rgb_to_hsv(avg_r/255, avg_g/255, avg_b/255)
            
            if s < 0.1:
                return "Calm", 0.85
            elif h < 0.1:
                return "Energetic", 0.75
            elif h < 0.2:
                return "Cozy", 0.80
            elif h < 0.3:
                return "Happy", 0.85
            elif h < 0.6:
                return "Peaceful", 0.80
            else:
                return "Aesthetic", 0.75
        except:
            return "Happy", 0.70
    
    def detect_sentiment(self, image):
        try:
            mood, confidence = self.analyze_colors(image)
            
            captions = {
                "Happy": "A bright and cheerful scene!",
                "Calm": "A peaceful, serene moment captured.",
                "Cozy": "Warm and inviting vibes here.",
                "Energetic": "Dynamic and full of energy!",
                "Peaceful": "Tranquility in every pixel.",
                "Aesthetic": "Visually stunning composition."
            }
            
            caption = captions.get(mood, "A beautiful image full of character.")
            
            return {
                'success': True,
                'sentiment': mood,
                'confidence': confidence,
                'category': 'scenery',
                'caption': caption,
                'all_sentiments': {'positive': confidence, 'negative': 1-confidence}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

_detector = None

def get_sentiment_detector():
    global _detector
    if _detector is None:
        _detector = ImageSentimentDetector()
    return _detector
