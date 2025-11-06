"""
Utility functions for Streamlit UI
"""
import streamlit as st

def show_cache_info(cache_source: str, response_time: float):
    """Display cache information in a formatted way"""
    if cache_source == "memcache":
        st.success(f"⚡ Ultra-fast response from Memcached! ({response_time:.2f}ms)")
    elif cache_source == "redis":
        st.success(f"🚀 Fast response from Redis! ({response_time:.2f}ms)")
    else:
        st.info(f"🤖 Fresh response from AI model ({response_time:.2f}ms)")
        st.caption("💡 Try the same request again to see caching magic!")

def format_metrics(col, label, value, help_text=None):
    """Display a metric in a formatted card"""
    with col:
        st.metric(label, value, help=help_text)

def show_error_message(error_msg: str):
    """Display error message with helpful information"""
    st.error(f"❌ Error: {error_msg}")
    
    if "Connection" in error_msg or "timeout" in error_msg.lower():
        st.warning("""
        ⚠️ **Connection Issue Detected**
        
        Please ensure:
        1. FastAPI server is running on http://127.0.0.1:8000
        2. Docker services (Redis, Memcached) are running
        3. Database connection is working
        
        Run: `python -m uvicorn app.main:app --reload`
        """)
