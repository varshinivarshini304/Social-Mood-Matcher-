"""
Google Gemini Service - Working Version
"""

import os
import google.generativeai as genai
from PIL import Image
import io
import traceback

class GeminiAnalyzer:
    def __init__(self):
        self.available = False
        self.model = None
        self.error_message = None
        self.load_model()
    
    def load_model(self):
        """Initialize Gemini API"""
        try:
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                self.error_message = "No GEMINI_API_KEY found in environment"
                print(self.error_message)
                return
            
            if not api_key.startswith("AIza"):
                self.error_message = "API key doesn't look valid (should start with AIza)"
                print(self.error_message)
                return
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Test the connection with a simple prompt
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Quick test to verify API works
            test_response = self.model.generate_content("Say 'OK' if you can hear me")
            if test_response and test_response.text:
                self.available = True
                print("✅ Gemini API initialized and working!")
            else:
                self.error_message = "API test failed - no response"
                
        except Exception as e:
            self.error_message = f"Init error: {str(e)}"
            print(f"Gemini init error: {e}")
            self.available = False
    
    def analyze_image_sentiment(self, image):
        """Analyze image using Gemini"""
        if not self.available:
            print(f"Gemini not available: {self.error_message}")
            return {
                'success': False, 
                'error': self.error_message or 'Gemini not available'
            }
        
        try:
            print("Starting Gemini image analysis...")
            
            # Convert PIL image to bytes
            if isinstance(image, Image.Image):
                pil_image = image
            else:
                pil_image = Image.fromarray(image)
            
            # Resize for faster processing
            max_size = 800
            if max(pil_image.size) > max_size:
                ratio = max_size / max(pil_image.size)
                new_size = (int(pil_image.size[0] * ratio), int(pil_image.size[1] * ratio))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"Resized image to {new_size}")
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='JPEG', quality=80)
            img_data = img_bytes.getvalue()
            print(f"Image converted to bytes: {len(img_data)} bytes")
            
            # Create prompt
            prompt = """Analyze this image and respond in EXACTLY this format:

MOOD: [one word: Happy, Calm, Cozy, Aesthetic, Energetic, Peaceful, Romantic, or Nostalgic]
CONFIDENCE: [number between 0 and 1]
CATEGORY: [food, scenery, people, or abstract]
DESCRIPTION: [2-3 sentences describing what you see in detail]

Example response:
MOOD: Happy
CONFIDENCE: 0.9
CATEGORY: scenery
DESCRIPTION: A beautiful sunset over mountains with orange and purple colors in the sky."""
            
            print("Calling Gemini API...")
            # Call Gemini
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_data}
            ])
            
            response_text = response.text
            print(f"Gemini response received: {response_text[:200]}...")
            
            # Parse response
            mood = "Happy"
            confidence = 0.8
            category = "scenery"
            description = "A beautiful image"
            
            lines = response_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('MOOD:'):
                    mood = line.replace('MOOD:', '').strip()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.replace('CONFIDENCE:', '').strip())
                    except:
                        confidence = 0.8
                elif line.startswith('CATEGORY:'):
                    category = line.replace('CATEGORY:', '').strip().lower()
                elif line.startswith('DESCRIPTION:'):
                    description = line.replace('DESCRIPTION:', '').strip()
            
            print(f"Parsed: mood={mood}, confidence={confidence}, category={category}")
            
            return {
                'success': True,
                'sentiment': mood,
                'confidence': confidence,
                'category': category,
                'caption': description,
                'all_sentiments': {'positive': confidence, 'negative': 1-confidence}
            }
            
        except Exception as e:
            print(f"Gemini analysis error: {traceback.format_exc()}")
            return {
                'success': False, 
                'error': str(e),
                'sentiment': 'Happy',
                'confidence': 0.7,
                'category': 'scenery',
                'caption': 'Analysis failed, using default'
            }

# Singleton
_analyzer = None

def get_gemini_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = GeminiAnalyzer()
    return _analyzer
