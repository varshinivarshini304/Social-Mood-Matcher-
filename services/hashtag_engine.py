class HashtagEngine:
    def __init__(self):
        self.trending = ['#Explore2024', '#TravelGoals', '#MakeMoments', '#CaptureTheVibe', '#SocialMoodMatcher']
    
    def get_hashtags_by_priority(self, category, sentiment, all_sentiments=None):
        hashtags = ['#Beautiful', '#Amazing', '#Vibes', '#Happy', '#Love']
        return hashtags + self.trending

_engine = None

def get_hashtag_engine():
    global _engine
    if _engine is None:
        _engine = HashtagEngine()
    return _engine
