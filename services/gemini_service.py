"""
Google Gemini Service for Enhanced Image Analysis
Properly analyzes images and generates captions based on content
"""

import os
import base64
from PIL import Image
import io
import google.generativeai as genai

class GeminiAnalyzer:
    def __init__(self):
        self.available = False
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Initialize Gemini API"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # Use gemini-1.5-flash for faster responses
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.available = True
                print("✅ Gemini API initialized successfully")
            else:
                print("❌ No Gemini API key found")
        except Exception as e:
            print(f"❌ Error loading Gemini: {e}")
            self.available = False
    
    def analyze_image_sentiment(self, image):
        """Analyze image and return sentiment based on actual content"""
        if not self.available:
            return {'success': False, 'error': 'Gemini not available'}
        
        try:
            # Prepare image
            if isinstance(image, Image.Image):
                pil_image = image
            else:
                pil_image = Image.fromarray(image)
            
            # Resize for faster processing
            pil_image.thumbnail((1024, 1024))
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85)
            img_bytes = img_byte_arr.getvalue()
            
            # Create prompt for detailed image analysis
            prompt = """You are an expert social media caption writer. Analyze this image and respond with a JSON object containing:

1. "sentiment": one word describing the mood (Happy, Calm, Cozy, Aesthetic, Energetic, Peaceful, Romantic, Nostalgic)
2. "confidence": number between 0 and 1
3. "category": either 'food' or 'scenery' or 'people' or 'abstract'
4. "caption": a detailed 2-3 sentence description of what you see in the image (be specific about objects, colors, actions, setting)
5. "vibe": a short phrase describing the overall feeling

Respond with ONLY valid JSON, no other text. Example format:
{
    "sentiment": "Happy",
    "confidence": 0.9,
    "category": "scenery",
    "caption": "A sunlit beach with gentle waves crashing on golden sand. Palm trees sway in the warm breeze.",
    "vibe": "Tropical paradise relaxation"
}"""
            
            # Call Gemini with image
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_bytes}
            ])
            
            # Parse JSON response
            import json
            import re
            
            # Clean response text (remove markdown if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            return {
                'success': True,
                'sentiment': result.get('sentiment', 'Happy'),
                'confidence': result.get('confidence', 0.8),
                'category': result.get('category', 'scenery'),
                'caption': result.get('caption', 'A beautiful image'),
                'vibe': result.get('vibe', 'Beautiful moment'),
                'all_sentiments': {'positive': result.get('confidence', 0.8), 'negative': 0.2}
            }
            
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return {
                'success': False,
                'error': str(e),
                'sentiment': 'Happy',
                'confidence': 0.7,
                'category': 'scenery',
                'caption': 'Unable to analyze image'
            }
    
    def generate_caption_variants(self, image, sentiment, category):
        """Generate multiple caption variants based on image content"""
        if not self.available:
            return {'aesthetic': 'Gemini not available'}
        
        try:
            # Prepare image
            if isinstance(image, Image.Image):
                pil_image = image
            else:
                pil_image = Image.fromarray(image)
            
            pil_image.thumbnail((1024, 1024))
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85)
            img_bytes = img_byte_arr.getvalue()
            
            prompt = f"""Based on this image which has a {sentiment} mood, generate 3 engaging social media captions.
            The captions should be specific to what's IN THE IMAGE (describe objects, colors, actions).
            
            Return ONLY JSON format:
            {{
                "casual": "casual, friendly caption with emojis",
                "aesthetic": "poetic, artistic caption with minimal emojis", 
                "punchy": "short, impactful caption under 100 characters"
            }}
            
            Make them specific to THIS image, not generic!"""
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_bytes}
            ])
            
            import json
            import re
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            print(f"Caption generation error: {e}")
            return {
                'casual': f"Enjoying this {sentiment.lower()} moment! ✨",
                'aesthetic': f"{sentiment} vibes captured. 🎨",
                'punchy': f"So {sentiment.lower()}! 🔥"
            }
    
    def get_visual_intelligence(self, image):
        """Get detailed visual analysis"""
        if not self.available:
            return {'colors': 'N/A', 'objects': 'N/A', 'tip': 'Enable Gemini API'}
        
        try:
            if isinstance(image, Image.Image):
                pil_image = image
            else:
                pil_image = Image.fromarray(image)
            
            pil_image.thumbnail((1024, 1024))
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85)
            img_bytes = img_byte_arr.getvalue()
            
            prompt = """Analyze this image and return JSON:
            {
                "colors": "list the 3 main colors",
                "objects": "list main objects/things visible",
                "tip": "one photography composition tip",
                "mood": "describe the mood"
            }"""
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_bytes}
            ])
            
            import json
            import re
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            return {
                'colors': 'Unable to analyze',
                'objects': 'Try again',
                'tip': 'Ensure good lighting',
                'mood': 'Unknown'
            }

# Singleton instance
_analyzer = None

def get_gemini_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = GeminiAnalyzer()
    return _analyzer
