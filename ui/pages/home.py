"""
Home Page - Dashboard Overview
"""
import streamlit as st
import requests
from datetime import datetime
import time

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def show():
    """Display home page with system overview"""
    
    st.header("🏠 Dashboard Overview")
    
    # Check API health with better error handling
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>✅ API Status</h3>
                    <h2>Online</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                memcache_status = health_data.get("memcached_connected", False)
                status_color = "🟢" if memcache_status else "🔴"
                status_text = "Connected" if memcache_status else "Disconnected"
                bg_color = "#2ecc71" if memcache_status else "#e74c3c"
                st.markdown(f"""
                <div class="metric-card" style="background: {bg_color};">
                    <h3>⚡ Memcached</h3>
                    <h2>{status_color} {status_text}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                redis_status = health_data.get("redis_connected", False)
                status_color = "🟢" if redis_status else "🔴"
                status_text = "Connected" if redis_status else "Disconnected"
                bg_color = "#2ecc71" if redis_status else "#e74c3c"
                st.markdown(f"""
                <div class="metric-card" style="background: {bg_color};">
                    <h3>💾 Redis</h3>
                    <h2>{status_color} {status_text}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                db_status = health_data.get("database_connected", False)
                status_color = "🟢" if db_status else "🔴"
                status_text = "Connected" if db_status else "Disconnected"
                bg_color = "#2ecc71" if db_status else "#e74c3c"
                st.markdown(f"""
                <div class="metric-card" style="background: {bg_color};">
                    <h3>🗄️ Database</h3>
                    <h2>{status_color} {status_text}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Show warning if services are disconnected
            if not (memcache_status and redis_status):
                st.warning("⚠️ **Cache services not connected!** Start Docker Desktop and run: `docker-compose up -d`")
        else:
            st.error("❌ Failed to connect to API")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Connection Error: {str(e)}")
        st.warning("⚠️ Make sure the FastAPI server is running on http://127.0.0.1:8000")
    
    st.markdown("---")
    
    # System Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Features")
        st.markdown("""
        #### Text Processing (Groq AI)
        - 📝 **Summarization**: Condense long texts
        - 💬 **Chat**: Interactive conversations
        - 😊 **Sentiment Analysis**: Detect emotions
        - 🌍 **Translation**: Multi-language support
        
        #### Image Processing (Groq Vision)
        - 🖼️ **Image Captioning**: Generate descriptions
        - 🏷️ **Image Classification**: Identify objects
        - 📤 **Upload Support**: Process your images
        """)
    
    with col2:
        st.subheader("⚡ Performance Boost")
        st.markdown("""
        #### Two-Layer Caching Architecture
        
        **Layer 1: Memcached (L1 Cache)**
        - ⚡ Ultra-fast: ~2ms response time
        - 🕐 TTL: 5 minutes
        - 💨 In-memory storage
        
        **Layer 2: Redis (L2 Cache)**
        - 🚀 Fast: ~12ms response time
        - 🕐 TTL: 1 hour
        - 💾 Persistent storage
        
        **Model Processing (Cold)**
        - 🐌 Slow: ~1200ms response time
        - 💰 Uses API credits
        - 🔄 Only when cache misses
        
        ### 📊 Speed Improvement
        **250-600× faster with cache hits!**
        """)
    
    st.markdown("---")
    
    # Quick Start Guide
    st.subheader("🚀 Quick Start")
    
    tab1, tab2, tab3 = st.tabs(["📝 Text", "🖼️ Image", "📊 Stats"])
    
    with tab1:
        st.markdown("""
        ### Try Text Processing
        1. Go to **📝 Text Processing** page
        2. Select a task (Summarization, Chat, etc.)
        3. Enter your text
        4. Click **Process** and see results!
        
        **First request**: Will query the AI model
        **Second request**: Lightning-fast cache response! ⚡
        """)
    
    with tab2:
        st.markdown("""
        ### Try Image Processing
        1. Go to **🖼️ Image Processing** page
        2. Choose Caption or Classification
        3. Upload an image or provide URL
        4. Get instant AI-powered results!
        
        **Powered by**: Groq Llama 4 Scout Vision Model
        """)
    
    with tab3:
        st.markdown("""
        ### View Statistics
        1. Go to **📊 Statistics** page
        2. See cache hit rates
        3. View response times
        4. Analyze performance metrics
        
        **Real-time insights** into your API usage!
        """)
    
    # Footer info
    st.markdown("---")
    st.info("💡 **Tip**: Try sending the same request twice to see the caching in action!")
