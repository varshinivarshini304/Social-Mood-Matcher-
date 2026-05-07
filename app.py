"""
Social Mood Matcher - AI Caption & Hashtag Generator
Main Streamlit application for generating AI-powered social media captions.
"""

import os
import sys
from pathlib import Path

# Streamlit Cloud optimization
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
from PIL import Image
# After loading models, add this debug code:
if st.session_state.use_gemini:
    gemini = get_gemini_analyzer()
    if gemini and gemini.available:
        st.success("✅ Gemini is ACTIVE and ready!")
    else:
        st.error("❌ Gemini failed to load. Check API key.")
# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import UI_CONFIG, CAPTION_STYLES, CHARACTER_LIMITS, USE_GEMINI, API_KEYS
from utils.image_utils import validate_and_load_image
from utils.text_utils import combine_caption_and_hashtags
from services.image_sentiment import get_sentiment_detector
from services.caption_generator import get_caption_generator
from services.hashtag_engine import get_hashtag_engine
from services.character_limiter import get_character_limiter
from services.gemini_service import get_gemini_analyzer


# Page configuration
st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["initial_sidebar_state"]
)

# Custom CSS
st.markdown("""
<style>    
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.3rem;
        margin-bottom: 2.5rem;
    }
    
    .sentiment-badge {
        display: inline-block;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1.4rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .caption-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 1.5rem 0;
        font-size: 1.4rem;
        line-height: 1.8;
        color: #1a1a1a;
        font-weight: 600;
    }
    
    .hashtag-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        color: #0d47a1;
        font-weight: 700;
        font-size: 1.3rem;
        border: 2px solid #2196f3;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 800;
        border: none;
        padding: 1rem;
        border-radius: 12px;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'sentiment_result' not in st.session_state:
        st.session_state.sentiment_result = None
    if 'generated_caption' not in st.session_state:
        st.session_state.generated_caption = None
    if 'generated_hashtags' not in st.session_state:
        st.session_state.generated_hashtags = None
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = 'casual'
    if 'models_loaded' not in st.session_state:
        st.session_state.models_loaded = False
    if 'use_gemini' not in st.session_state:
        st.session_state.use_gemini = USE_GEMINI
    if 'gemini_analyzer' not in st.session_state:
        st.session_state.gemini_analyzer = None
    if 'history' not in st.session_state:
        st.session_state.history = []


@st.cache_resource
def load_models():
    """Load AI models."""
    with st.spinner("Loading AI models..."):
        detector = get_sentiment_detector()
        generator = get_caption_generator()
        hashtag_engine = get_hashtag_engine()
        limiter = get_character_limiter()
    return detector, generator, hashtag_engine, limiter


def display_header():
    """Display application header."""
    st.markdown('<h1 class="main-header">🎭 Social Mood Matcher</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Caption & Hashtag Generator for Social Media</p>', unsafe_allow_html=True)
    st.markdown("---")


def display_sentiment_info(sentiment_result):
    """Display sentiment detection results - FIXED version."""
    st.markdown("### 🎭 Detected Vibe")
    
    # Handle different possible response formats
    if isinstance(sentiment_result, dict):
        # Try to get sentiment from different possible keys
        sentiment = sentiment_result.get('sentiment', 'Happy')
        if not sentiment:
            sentiment = sentiment_result.get('mood', 'Happy')
        confidence = sentiment_result.get('confidence', 0.8)
        category = sentiment_result.get('category', 'scenery')
        caption = sentiment_result.get('caption', 'A beautiful image')
    else:
        sentiment = 'Happy'
        confidence = 0.8
        category = 'scenery'
        caption = 'A beautiful image'
    
    sentiment = sentiment.capitalize() if sentiment else 'Happy'
    
    # Color based on sentiment
    sentiment_colors = {
        "Happy": "#FFD700", "Calm": "#87CEEB", "Cozy": "#FFA07A",
        "Aesthetic": "#DDA0DD", "Energetic": "#FF6347", "Peaceful": "#98FB98"
    }
    color = sentiment_colors.get(sentiment, "#667eea")
    
    st.markdown(
        f'<div class="sentiment-badge" style="background-color: {color}; color: white;">'
        f'{sentiment} <span style="font-size: 1rem;">({confidence:.1%} confidence)</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.markdown(f"**Category:** {category.capitalize()}")
    
    with st.expander("📝 AI Image Description"):
        st.write(caption)


def display_caption_and_hashtags(caption, hashtags, platform="twitter"):
    """Display generated caption and hashtags."""
    st.markdown("### ✨ Generated Content")
    
    st.markdown(f'<div class="caption-box">{caption}</div>', unsafe_allow_html=True)
    
    if hashtags:
        hashtag_string = ' '.join(hashtags) if isinstance(hashtags, list) else hashtags
        st.markdown(f'<div class="hashtag-box">{hashtag_string}</div>', unsafe_allow_html=True)
    
    # Copy button
    combined_text = f"{caption}\n\n{' '.join(hashtags) if hashtags else ''}"
    st.code(combined_text, language=None)
    st.info("💡 Copy the text above to share on social media!")


def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    
    # Load models
    detector, generator, hashtag_engine, limiter = load_models()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        selected_style = st.selectbox(
            "Caption Style",
            options=list(CAPTION_STYLES.keys()),
            format_func=lambda x: x.capitalize(),
            index=list(CAPTION_STYLES.keys()).index(st.session_state.selected_style)
        )
        st.session_state.selected_style = selected_style
        
        style_info = CAPTION_STYLES[selected_style]
        st.markdown(f"**Tone:** {style_info['tone']}")
        st.markdown(f"**Formality:** {style_info['formality']}")
        
        st.markdown("---")
        
        platform = st.selectbox(
            "Platform",
            options=["twitter", "instagram", "facebook"],
            format_func=lambda x: x.capitalize()
        )
        st.markdown(f"**Character Limit:** {CHARACTER_LIMITS[platform]}")
        
        st.markdown("---")
        
        num_hashtags = st.slider("Number of hashtags", min_value=3, max_value=10, value=6)
        
        st.markdown("---")
        
        # Gemini toggle
        gemini_available = API_KEYS.get("gemini") is not None
        
        if gemini_available:
            use_gemini = st.toggle("Use Google Gemini API", value=st.session_state.use_gemini)
            st.session_state.use_gemini = use_gemini
            if use_gemini:
                st.success("✨ Using Gemini API (Enhanced)")
            else:
                st.info("🔧 Using Local Models")
        else:
            st.warning("⚠️ Gemini API key not configured")
            st.session_state.use_gemini = False
        
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Social Mood Matcher** uses AI to:
            - 🎭 Detect image sentiment
            - ✍️ Generate engaging captions
            - #️⃣ Suggest hashtags
            """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=UI_CONFIG["supported_formats"],
            help=f"Max size: {UI_CONFIG['max_upload_size_mb']}MB"
        )
        
        if uploaded_file:
            image, error = validate_and_load_image(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                if st.button("🚀 Generate Caption & Hashtags", type="primary"):
                    with st.spinner("🔮 Analyzing image..."):
                        try:
                            sentiment_result = None
                            caption = None
                            
                            if st.session_state.use_gemini and gemini_available:
                                if st.session_state.gemini_analyzer is None:
                                    st.session_state.gemini_analyzer = get_gemini_analyzer()
                                
                                gemini = st.session_state.gemini_analyzer
                                if gemini and gemini.available:
                                    sentiment_result = gemini.analyze_image_sentiment(image)
                                    if sentiment_result and sentiment_result.get('success'):
                                        caption = sentiment_result.get('caption', '')
                                    
                                    if not caption:
                                        st.warning("Gemini API error, falling back to local models")
                                        sentiment_result = None
                            
                            if not sentiment_result or not caption:
                                # Fallback to local
                                sentiment_result = detector.detect_sentiment(image)
                                if sentiment_result and sentiment_result.get('success'):
                                    caption = generator.generate_caption(
                                        sentiment=sentiment_result.get('sentiment', 'Happy'),
                                        style=selected_style,
                                        image_caption=sentiment_result.get('caption', 'this beautiful scene'),
                                        category=sentiment_result.get('category', 'scenery')
                                    )
                            
                            if caption and sentiment_result:
                                st.session_state.sentiment_result = sentiment_result
                                
                                # Generate hashtags
                                hashtags = hashtag_engine.get_hashtags_by_priority(
                                    category=sentiment_result.get('category', 'scenery'),
                                    sentiment=sentiment_result.get('sentiment', 'Happy'),
                                    all_sentiments={}
                                )[:num_hashtags]
                                
                                st.session_state.generated_caption = caption
                                st.session_state.generated_hashtags = hashtags
                                
                                # Add to history
                                st.session_state.history.insert(0, {
                                    "caption": caption,
                                    "hashtags": hashtags,
                                    "sentiment": sentiment_result.get('sentiment', 'Happy')
                                })
                                
                                st.success("✅ Content generated successfully!")
                            else:
                                st.error("Failed to generate content. Please try again.")
                                
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### 📊 AI Results")
        
        tab_basic, tab_history = st.tabs(["✨ Content", "📜 History"])
        
        with tab_basic:
            if st.session_state.sentiment_result and st.session_state.generated_caption:
                display_sentiment_info(st.session_state.sentiment_result)
                display_caption_and_hashtags(
                    st.session_state.generated_caption,
                    st.session_state.generated_hashtags,
                    platform
                )
                
                full_text = f"{st.session_state.generated_caption}\n\n{' '.join(st.session_state.generated_hashtags)}"
                st.download_button(
                    label="💾 Download",
                    data=full_text,
                    file_name="caption.txt",
                    mime="text/plain"
                )
            else:
                st.info("👆 Upload an image and click 'Generate'!")
        
        with tab_history:
            if st.session_state.history:
                for i, item in enumerate(st.session_state.history[:5]):
                    with st.expander(f"#{i+1} - {item.get('sentiment', 'Unknown')}"):
                        st.write(item.get('caption', ''))
                        st.caption(" ".join(item.get('hashtags', [])))
            else:
                st.write("No history yet.")


if __name__ == "__main__":
    main()
