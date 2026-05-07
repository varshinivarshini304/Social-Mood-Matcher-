class CaptionGenerator:
    def __init__(self):
        pass
    
    def generate_caption(self, sentiment, style, image_caption, category):
        templates = {
            'Happy': {
                'casual': f"✨ {image_caption} This made my day so much brighter! 🥰",
                'aesthetic': f"Chasing golden moments. {image_caption}",
                'professional': f"Captured at its finest moment.",
                'playful': f"OMG this is EVERYTHING! Can't get enough! 😍✨"
            },
            'Calm': {
                'casual': f"Taking a moment to appreciate this. Peaceful vibes only. 🧘‍♀️",
                'aesthetic': f"Soft moments, quiet soul.",
                'professional': f"Finding tranquility in this moment.",
                'playful': f"Shhh... this is giving main character energy! 💫"
            },
            'Cozy': {
                'casual': f"Wrapped in warmth with this view. Pure comfort! 🏠☕",
                'aesthetic': f"Warmth cascades through every corner.",
                'professional': f"Creating comfortable spaces.",
                'playful': f"Cozy season is HERE! This is my new best friend! 🧸✨"
            },
            'Aesthetic': {
                'casual': f"The vibes are immaculate here. 🎨✨",
                'aesthetic': f"Visual poetry in motion.",
                'professional': f"Art meets reality.",
                'playful': f"Warning: extreme aesthetics ahead! This is ART! 🎭✨"
            }
        }
        
        if sentiment not in templates:
            sentiment = 'Happy'
        
        return templates[sentiment].get(style, templates[sentiment]['casual'])

_generator = None

def get_caption_generator():
    global _generator
    if _generator is None:
        _generator = CaptionGenerator()
    return _generator
