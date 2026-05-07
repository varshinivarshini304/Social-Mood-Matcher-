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
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
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
        margin: 1rem 0;
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
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stAlert {
        border-radius: 10px;
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
    if 'gemini_status' not in st.session_state:
        st.session_state.gemini_status = "checking"


@st.cache_resource
def load_services():
    """Load all services"""
    detector = get_sentiment_detector()
    generator = get_caption_generator()
    hashtag_engine = get_hashtag_engine()
    limiter = get_character_limiter()
    gemini = get_gemini_analyzer()
    return {
        'detector': detector,
        'generator': generator,
        'hashtag_engine': hashtag_engine,
        'limiter': limiter,
        'gemini': gemini
    }


def display_header():
    """Display header"""
    st.markdown('<h1 class="main-header">🎭 Social Mood Matcher</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Caption & Hashtag Generator for Social Media</p>', unsafe_allow_html=True)
    st.markdown("---")


def display_sentiment_info(result):
    """Display sentiment results"""
    st.markdown("### 🎭 Detected Vibe")
    
    sentiment = result.get('sentiment', 'Happy')
    confidence = result.get('confidence', 0.8)
    category = result.get('category', 'scenery')
    description = result.get('caption', 'A beautiful image')
    
    sentiment_colors = {
        "Happy": "#FFD700",
        "Calm": "#87CEEB", 
        "Cozy": "#FFA07A",
        "Aesthetic": "#DDA0DD",
        "Energetic": "#FF6347",
        "Peaceful": "#98FB98",
        "Romantic": "#FF69B4",
        "Nostalgic": "#D2B48C"
    }
    
    color = sentiment_colors.get(sentiment, "#667eea")
    
    st.markdown(
        f'<div class="sentiment-badge" style="background: {color}; color: white;">'
        f'{sentiment} ({confidence:.0%})</div>', 
        unsafe_allow_html=True
    )
    
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
    
    # Check Gemini availability
    gemini_available = gemini.available if gemini else False
    
    # Display Gemini status in sidebar
    if gemini_available:
        st.session_state.gemini_status = "available"
    else:
        st.session_state.gemini_status = "unavailable"
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Caption style
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
        
        # Platform
        platform = st.selectbox(
            "Platform",
            options=["twitter", "instagram", "facebook"],
            format_func=lambda x: x.capitalize()
        )
        st.markdown(f"**Character Limit:** {CHARACTER_LIMITS[platform]}")
        
        st.markdown("---")
        
        # Hashtags count
        num_hashtags = st.slider("Number of hashtags", min_value=3, max_value=10, value=6)
        
        st.markdown("---")
        
        # Gemini toggle
        if gemini_available:
            use_gemini = st.toggle(
                "✨ Use Google Gemini API", 
                value=st.session_state.use_gemini,
                help="Toggle to use Gemini for better image analysis and captions"
            )
            st.session_state.use_gemini = use_gemini
            
            if use_gemini:
                st.success("🚀 Gemini API Active!")
                st.caption("Enhanced image analysis enabled")
            else:
                st.info("🔧 Local Mode Active")
        else:
            st.warning("⚠️ Gemini API not configured")
            st.caption("Add GEMINI_API_KEY to Secrets to enable")
            st.session_state.use_gemini = False
        
        st.markdown("---")
        
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Social Mood Matcher** uses AI to:
            - 🎭 Detect image sentiment
            - ✍️ Generate engaging captions  
            - #️⃣ Suggest relevant hashtags
            - 📏 Ensure character limits
            
            **Powered by:**
            - Google Gemini API (optional)
            - Custom AI models
            - Trending hashtags
            """)
    
    # Main content area - Two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=UI_CONFIG["supported_formats"],
            help=f"Max size: {UI_CONFIG['max_upload_size_mb']}MB"
        )
        
        if uploaded_file:
            # Validate and load image
            image, error = validate_and_load_image(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            else:
                # Display image
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Generate button
                if st.button("🚀 Generate Caption & Hashtags", type="primary"):
                    with st.spinner("🔮 Analyzing image and generating content..."):
                        try:
                            sentiment_result = None
                            caption = None
                            
                            # Try Gemini if enabled
                            if st.session_state.use_gemini and gemini_available:
                                st.info("🤖 Using Gemini AI for analysis...")
                                sentiment_result = gemini.analyze_image_sentiment(image)
                                
                                if sentiment_result and sentiment_result.get('success'):
                                    image_description = sentiment_result.get('caption', '')
                                    sentiment = sentiment_result.get('sentiment', 'Happy')
                                    category = sentiment_result.get('category', 'scenery')
                                    
                                    caption = generator.generate_caption(
                                        sentiment=sentiment,
                                        style=selected_style,
                                        image_caption=image_description,
                                        category=category
                                    )
                                    st.session_state.sentiment_result = sentiment_result
                                    st.success("✅ Gemini analysis complete!")
                                else:
                                    st.warning("⚠️ Gemini error, falling back to local models...")
                                    st.session_state.use_gemini = False
                            
                            # Fallback to local models
                            if not st.session_state.use_gemini or not caption:
                                sentiment_result = detector.detect_sentiment(image)
                                
                                if sentiment_result and sentiment_result.get('success'):
                                    caption = generator.generate_caption(
                                        sentiment=sentiment_result.get('sentiment', 'Happy'),
                                        style=selected_style,
                                        image_caption=sentiment_result.get('caption', 'this beautiful scene'),
                                        category=sentiment_result.get('category', 'scenery')
                                    )
                                    st.session_state.sentiment_result = sentiment_result
                            
                            if caption and sentiment_result:
                                # Generate hashtags
                                hashtags_result = hashtag_engine.get_hashtags_by_priority(
                                    category=sentiment_result.get('category', 'scenery'),
                                    sentiment=sentiment_result.get('sentiment', 'Happy'),
                                    all_sentiments={}
                                )
                                
                                # Handle hashtags
                                if isinstance(hashtags_result, list):
                                    hashtags = hashtags_result[:num_hashtags]
                                else:
                                    hashtags = ['#Beautiful', '#Amazing', '#Vibes', '#Happy', '#Love', '#Explore2024']
                                
                                st.session_state.generated_caption = caption
                                st.session_state.generated_hashtags = hashtags
                                
                                # Add to history
                                st.session_state.history.insert(0, {
                                    'caption': caption,
                                    'hashtags': hashtags,
                                    'sentiment': sentiment_result.get('sentiment', 'Happy'),
                                    'timestamp': 'Just now'
                                })
                                
                                st.success("✅ Content generated successfully!")
                            else:
                                st.error("❌ Failed to generate content. Please try again.")
                                
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            st.info("💡 Try refreshing the page or uploading a different image")
    
    with col2:
        st.markdown("### 📊 AI Results")
        
        # Tabs for different views
        tab_basic, tab_history = st.tabs(["✨ Content", "📜 History"])
        
        with tab_basic:
            if st.session_state.sentiment_result and st.session_state.generated_caption:
                display_sentiment_info(st.session_state.sentiment_result)
                
                # Display caption
                st.markdown('<div class="caption-box">' + st.session_state.generated_caption + '</div>', unsafe_allow_html=True)
                
                # Display hashtags
                hashtag_string = ' '.join(st.session_state.generated_hashtags) if isinstance(st.session_state.generated_hashtags, list) else st.session_state.generated_hashtags
                st.markdown('<div class="hashtag-box">' + hashtag_string + '</div>', unsafe_allow_html=True)
                
                # Combined text for copying
                full_text = f"{st.session_state.generated_caption}\n\n{hashtag_string}"
                st.code(full_text, language=None)
                st.info("💡 Copy the text above to share on social media!")
                
                # Download button
                st.download_button(
                    label="💾 Download as Text",
                    data=full_text,
                    file_name="social_media_caption.txt",
                    mime="text/plain"
                )
            else:
                st.info("👆 Upload an image and click 'Generate' to see results!")
                st.markdown("""
                ### 💡 Tips for best results:
                - Use clear, well-lit images
                - Food photos work well for food detection
                - Landscapes work well for scenery detection
                - Turn on Gemini API for better quality
                """)
        
        with tab_history:
            if st.session_state.history:
                st.markdown("### Recent Generations")
                for i, item in enumerate(st.session_state.history[:5]):
                    with st.expander(f"#{i+1} - {item.get('sentiment', 'Unknown')}"):
                        st.write(item.get('caption', ''))
                        st.caption(" ".join(item.get('hashtags', [])))
            else:
                st.write("No history yet. Generate your first caption!")


if __name__ == "__main__":
    main()
