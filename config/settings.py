"""
Configuration settings for Social Mood Matcher
"""

import os

# Character limits for social platforms
CHARACTER_LIMITS = {
    "twitter": 280,
    "instagram": 2200,
    "facebook": 63206
}

# Caption styles with descriptions
CAPTION_STYLES = {
    "casual": {
        "tone": "Friendly and relaxed",
        "formality": "Low",
        "emoji": "Moderate"
    },
    "aesthetic": {
        "tone": "Artistic and poetic",
        "formality": "Medium",
        "emoji": "Minimal"
    },
    "professional": {
        "tone": "Polished and informative",
        "formality": "High",
        "emoji": "None"
    },
    "playful": {
        "tone": "Fun and energetic",
        "formality": "Low",
        "emoji": "High"
    }
}

# UI Configuration
UI_CONFIG = {
    "page_title": "Social Mood Matcher",
    "page_icon": "🎭",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "supported_formats": ["jpg", "jpeg", "png", "webp"],
    "max_upload_size_mb": 10
}

# Model settings
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY", None)
}
DEVICE = -1  # -1 = CPU, 0 = GPU
