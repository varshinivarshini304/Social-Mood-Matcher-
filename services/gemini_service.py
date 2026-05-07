class GeminiAnalyzer:
    def __init__(self):
        self.available = False
    
    def analyze_image_sentiment(self, image):
        return {'success': False, 'error': 'Gemini not configured'}

def get_gemini_analyzer():
    return GeminiAnalyzer()
