"""
Google Gemini Service - Fixed for Streamlit Cloud
"""

import os
import google.generativeai as genai
from PIL import Image
import io

class GeminiAnalyzer:
    def __init__(self):
        self.available = False
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Initialize Gemini API"""
        try:
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                print("No Gemini API key found")
                return
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Use the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.available = True
            print("✅ Gemini API initialized!")
            
        except Exception as e:
            print(f"Gemini init error: {e}")
            self.available = False
    
    def analyze_image_sentiment(self, image):
        """Analyze image using Gemini"""
        if not self.available:
            return {'success': False, 'error': 'Gemini not available'}
        
        try:
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
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='JPEG', quality=80)
            img_data = img_bytes.getvalue()
            
            # Create prompt
            prompt = """Look at this image and tell me:
            1. What do you see? (describe the main objects/people/scene)
            2. What mood does it have? (choose one: Happy, Calm, Cozy, Aesthetic, Energetic, Peaceful)
            
            Respond in this exact format:
            MOOD: [mood word]
            DESCRIPTION: [2-3 sentence description of what you see]"""
            
            # Call Gemini
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_data}
            ])
            
            response_text = response.text
            
            # Parse response
            mood = "Happy"
            description = "A beautiful image"
            
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith('MOOD:'):
                    mood = line.replace('MOOD:', '').strip()
                elif line.startswith('DESCRIPTION:'):
                    description = line.replace('DESCRIPTION:', '').strip()
            
            return {
                'success': True,
                'sentiment': mood,
                'confidence': 0.9,
                'category': 'scenery',
                'caption': description,
                'all_sentiments': {'positive': 0.9, 'negative': 0.1}
            }
            
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return {'success': False, 'error': str(e)}

# Singleton
_analyzer = None

def get_gemini_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = GeminiAnalyzer()
    return _analyzer
