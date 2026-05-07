"""
Text Processing Utilities
"""

def combine_caption_and_hashtags(caption, hashtags):
    """Combine caption and hashtags into final text"""
    if isinstance(hashtags, list):
        hashtag_str = ' '.join(hashtags)
    else:
        hashtag_str = hashtags
    
    return f"{caption}\n\n{hashtag_str}"
