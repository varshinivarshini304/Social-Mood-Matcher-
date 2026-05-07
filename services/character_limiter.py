class CharacterLimiter:
    def __init__(self):
        self.limits = {'twitter': 280, 'instagram': 2200, 'facebook': 63206}
    
    def limit_text(self, caption, hashtags, platform):
        return caption, hashtags, True
    
    def get_character_stats(self, text, platform):
        limit = self.limits.get(platform, 280)
        return {'character_count': len(text), 'character_limit': limit, 'percentage_used': (len(text)/limit)*100}

_limiter = None

def get_character_limiter():
    global _limiter
    if _limiter is None:
        _limiter = CharacterLimiter()
    return _limiter
