"""
Streamlit UI for AI Response Caching System
Main application entry point
"""
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="AI Response Caching System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🚀 AI Response Caching System</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select a feature:",
    ["🏠 Home", "📝 Text Processing", "🖼️ Image Processing", "📊 Statistics", "⚙️ Settings"]
)

# Import page modules
from ui.pages import home, text_processing, image_processing, statistics, settings

# Route to selected page
if page == "🏠 Home":
    home.show()
elif page == "📝 Text Processing":
    text_processing.show()
elif page == "🖼️ Image Processing":
    image_processing.show()
elif page == "📊 Statistics":
    statistics.show()
elif page == "⚙️ Settings":
    settings.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 💡 About
- **Two-Layer Caching**: Memcached + Redis
- **AI Provider**: Groq API
- **Database**: PostgreSQL (Neon)
- **Version**: 1.0.0
""")
