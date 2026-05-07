import os

CHARACTER_LIMITS = {
    "twitter": 280,
    "instagram": 2200,
    "facebook": 63206
}

CAPTION_STYLES = {
    "casual": {"tone": "Friendly and relaxed", "formality": "Low"},
    "aesthetic": {"tone": "Artistic and poetic", "formality": "Medium"},
    "professional": {"tone": "Polished and informative", "formality": "High"},
    "playful": {"tone": "Fun and energetic", "formality": "Low"}
}

UI_CONFIG = {
    "page_title": "Social Mood Matcher",
    "page_icon": "🎭",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "supported_formats": ["jpg", "jpeg", "png", "webp"],
    "max_upload_size_mb": 10
}
