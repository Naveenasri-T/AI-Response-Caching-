"""
Settings Page
"""
import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def show():
    """Display settings and configuration"""
    
    st.header("⚙️ System Settings")
    
    # API Configuration
    st.subheader("🔌 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_url = st.text_input(
            "API Base URL",
            value=API_BASE_URL,
            help="The base URL of your FastAPI backend"
        )
    
    with col2:
        st.text_input(
            "API Version",
            value="v1",
            disabled=True,
            help="Current API version"
        )
    
    # Cache Configuration
    st.markdown("---")
    st.subheader("💾 Cache Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Memcached (L1 Cache)**
        - Host: localhost
        - Port: 11211
        - TTL: 300 seconds (5 minutes)
        - Status: 🟢 Active
        """)
    
    with col2:
        st.markdown("""
        **Redis (L2 Cache)**
        - Host: localhost
        - Port: 6379
        - TTL: 3600 seconds (1 hour)
        - Status: 🟢 Active
        """)
    
    # Database Configuration
    st.markdown("---")
    st.subheader("🗄️ Database Configuration")
    
    st.markdown("""
    **PostgreSQL (Neon DB)**
    - Type: Cloud PostgreSQL
    - Connection: SSL Required
    - Status: 🟢 Connected
    """)
    
    # AI Model Configuration
    st.markdown("---")
    st.subheader("🤖 AI Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Text Processing**
        - Provider: Groq
        - Model: llama-3.1-8b-instant
        - Context: 8K tokens
        - Status: 🟢 Active
        """)
    
    with col2:
        st.markdown("""
        **Image Processing**
        - Provider: Groq Vision
        - Model: Llama 4 Scout (17B)
        - Context: 128K tokens
        - Max Images: 5 per request
        - Status: 🟢 Active
        """)
    
    # System Health Check
    st.markdown("---")
    st.subheader("🏥 System Health Check")
    
    if st.button("🔍 Check System Health", type="primary"):
        with st.spinner("Checking system health..."):
            try:
                response = requests.get(f"{api_url}/health", timeout=5)
                
                if response.status_code == 200:
                    health = response.json()
                    
                    st.success("✅ System is healthy!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        status = "🟢 Online" if health.get("status") == "healthy" else "🔴 Offline"
                        st.metric("API Status", status)
                    
                    with col2:
                        memcache = "🟢 Connected" if health.get("memcache_connected") else "🔴 Disconnected"
                        st.metric("Memcached", memcache)
                    
                    with col3:
                        redis = "🟢 Connected" if health.get("redis_connected") else "🔴 Disconnected"
                        st.metric("Redis", redis)
                    
                    with col4:
                        db = "🟢 Connected" if health.get("db_connected") else "🔴 Disconnected"
                        st.metric("Database", db)
                    
                    # Display timestamp
                    st.caption(f"Last checked: {health.get('timestamp', 'N/A')}")
                
                else:
                    st.error(f"Health check failed: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection Error: {str(e)}")
                st.warning("Make sure the FastAPI server is running on " + api_url)
    
    # Documentation
    st.markdown("---")
    st.subheader("📚 Documentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Quick Links**
        - [FastAPI Docs](http://127.0.0.1:8000/docs)
        - [ReDoc](http://127.0.0.1:8000/redoc)
        - [GitHub Repository](#)
        """)
    
    with col2:
        st.markdown("""
        **Support**
        - [Report an Issue](#)
        - [Feature Request](#)
        - [API Reference](#)
        """)
    
    # About
    st.markdown("---")
    st.subheader("ℹ️ About")
    
    st.info("""
    **AI Response Caching System**
    
    Version: 1.0.0
    
    A production-ready AI response caching system with two-layer architecture:
    - Memcached (L1) for ultra-fast in-memory caching
    - Redis (L2) for persistent caching
    - Groq AI for text and image processing
    - PostgreSQL for request logging and analytics
    
    Built with ❤️ using FastAPI and Streamlit
    """)
