"""
Social Mood Matcher - AI Caption & Hashtag Generator
"""

import os
import sys
from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import UI_CONFIG, CAPTION_STYLES, CHARACTER_LIMITS
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
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sentiment-badge {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .caption-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 1rem 0;
        font-size: 1.2rem;
        line-height: 1.6;
    }
    
    .hashtag-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 15px;
        color: #0d47a1;
        font-weight: 700;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 800;
        border: none;
        padding: 0.8rem;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'sentiment_result' not in st.session_state:
        st.session_state.sentiment_result = None
    if 'generated_caption' not in st.session_state:
        st.session_state.generated_caption = None
    if 'generated_hashtags' not in st.session_state:
        st.session_state.generated_hashtags = None
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = 'casual'
    if 'use_gemini' not in st.session_state:
        st.session_state.use_gemini = False
    if 'history' not in st.session_state:
        st.session_state.history = []


@st.cache_resource
def load_services():
    """Load all services"""
    return {
        'detector': get_sentiment_detector(),
        'generator': get_caption_generator(),
        'hashtag_engine': get_hashtag_engine(),
        'limiter': get_character_limiter(),
        'gemini': get_gemini_analyzer()
    }


def display_header():
    st.markdown('<h1 class="main-header">🎭 Social Mood Matcher</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center">AI-Powered Caption & Hashtag Generator</p>', unsafe_allow_html=True)
    st.markdown("---")


def display_sentiment_info(result):
    """Display sentiment results"""
    st.markdown("### 🎭 Detected Vibe")
    
    sentiment = result.get('sentiment', 'Happy')
    confidence = result.get('confidence', 0.8)
    category = result.get('category', 'scenery')
    description = result.get('caption', 'A beautiful image')
    
    colors = {"Happy": "#FFD700", "Calm": "#87CEEB", "Cozy": "#FFA07A", 
              "Aesthetic": "#DDA0DD", "Energetic": "#FF6347", "Peaceful": "#98FB98"}
    color = colors.get(sentiment, "#667eea")
    
    st.markdown(f'<div class="sentiment-badge" style="background: {color}; color: white;">{sentiment} ({confidence:.0%})</div>', unsafe_allow_html=True)
    st.markdown(f"**Category:** {category.capitalize()}")
    
    with st.expander("📝 AI Image Description"):
        st.write(description)


def main():
    """Main application"""
    init_session_state()
    display_header()
    
    # Load services
    services = load_services()
    detector = services['detector']
    generator = services['generator']
    hashtag_engine = services['hashtag_engine']
    limiter = services['limiter']
    gemini = services['gemini']
    
    # Check if Gemini is available
    gemini_available = gemini.available if gemini else False
    
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
        
        num_hashtags = st.slider("Number of hashtags", 3, 10, 6)
        
        st.markdown("---")
        
        # Gemini toggle
        if gemini_available:
            use_gemini = st.toggle("✨ Use Google Gemini API", value=st.session_state.use_gemini)
            st.session_state.use_gemini = use_gemini
            if use_gemini:
                st.success("Gemini API Active! 🚀")
            else:
                st.info("Local Mode Active")
        else:
            st.warning("⚠️ Gemini API not configured")
            st.session_state.use_gemini = False
        
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Social Mood Matcher** uses AI to:
            - 🎭 Detect image sentiment
            - ✍️ Generate engaging captions
            - #️⃣ Suggest relevant hashtags
            """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=UI_CONFIG["supported_formats"]
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
                            
                            # Try Gemini first if enabled
                            if st.session_state.use_gemini and gemini_available:
                                st.info("🤖 Using Gemini AI for analysis...")
                                sentiment_result = gemini.analyze_image_sentiment(image)
                                
                                if sentiment_result and sentiment_result.get('success'):
                                    # Get the image description from Gemini
                                    image_description = sentiment_result.get('caption', '')
                                    sentiment = sentiment_result.get('sentiment', 'Happy')
                                    category = sentiment_result.get('category', 'scenery')
                                    
                                    # Generate caption using Gemini's description
                                    caption = generator.generate_caption(
                                        sentiment=sentiment,
                                        style=selected_style,
                                        image_caption=image_description,
                                        category=category
                                    )
                                    
                                    st.session_state.sentiment_result = sentiment_result
                                else:
                                    st.warning("Gemini error, falling back to local...")
                                    st.session_state.use_gemini = False
                            
                            # Fallback to local
                            if not st.session_state.use_gemini or not caption:
                                sentiment_result = detector.detect_sentiment(image)
                                if sentiment_result and sentiment_result.get('success'):
                                    caption = generator.generate_caption(
                                        sentiment=sentiment_result.get('sentiment', 'Happy'),
                                        style=selected_style,
                                        image_caption=sentiment_result.get('caption', 'this scene'),
                                        category=sentiment_result.get('category', 'scenery')
                                    )
                                    st.session_state.sentiment_result = sentiment_result
                            
                            if caption and sentiment_result:
                                # Generate hashtags
                                hashtags_list = hashtag_engine.get_hashtags_by_priority(
                                    category=sentiment_result.get('category', 'scenery'),
                                    sentiment=sentiment_result.get('sentiment', 'Happy'),
                                    all_sentiments={}
                                )
                                
                                # Limit hashtags
                                if isinstance(hashtags_list, list):
                                    hashtags = hashtags_list[:num_hashtags]
                                else:
                                    hashtags = [hashtags_list] if hashtags_list else ['#Beautiful']
                                
                                st.session_state.generated_caption = caption
                                st.session_state.generated_hashtags = hashtags
                                
                                # Add to history
                                st.session_state.history.insert(0, {
                                    'caption': caption,
                                    'hashtags': hashtags,
                                    'sentiment': sentiment_result.get('sentiment', 'Happy'),
                                    'time': 'Just now'
                                })
                                
                                st.success("✅ Caption generated successfully!")
                            else:
                                st.error("Failed to generate caption. Please try again.")
                                
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### 📊 Results")
        
        tab1, tab2 = st.tabs(["✨ Content", "📜 History"])
        
        with tab1:
            if st.session_state.sentiment_result and st.session_state.generated_caption:
                display_sentiment_info(st.session_state.sentiment_result)
                
                st.markdown(f'<div class="caption-box">{st.session_state.generated_caption}</div>', unsafe_allow_html=True)
                
                hashtag_str = ' '.join(st.session_state.generated_hashtags) if isinstance(st.session_state.generated_hashtags, list) else st.session_state.generated_hashtags
                st.markdown(f'<div class="hashtag-box">{hashtag_str}</div>', unsafe_allow_html=True)
                
                full_text = f"{st.session_state.generated_caption}\n\n{hashtag_str}"
                st.code(full_text, language=None)
                st.info("💡 Copy the text above to share!")
            else:
                st.info("👆 Upload an image and click Generate!")
        
        with tab2:
            if st.session_state.history:
                for i, item in enumerate(st.session_state.history[:5]):
                    with st.expander(f"#{i+1} - {item.get('sentiment', 'Unknown')}"):
                        st.write(item.get('caption', ''))
                        st.caption(' '.join(item.get('hashtags', [])))
            else:
                st.write("No history yet.")


if __name__ == "__main__":
    main()
