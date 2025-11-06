"""
Text Processing Page
"""
import streamlit as st
import requests
import json
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def show():
    """Display text processing interface"""
    
    st.header("📝 Text Processing with Groq AI")
    
    # Task selection
    task = st.selectbox(
        "Select Task",
        ["Summarization", "Chat", "Sentiment Analysis", "Translation"],
        help="Choose the AI task you want to perform"
    )
    
    # Task-specific inputs
    if task == "Summarization":
        show_summarization()
    elif task == "Chat":
        show_chat()
    elif task == "Sentiment Analysis":
        show_sentiment()
    elif task == "Translation":
        show_translation()

def show_summarization():
    """Summarization interface"""
    st.subheader("📝 Text Summarization")
    
    text = st.text_area(
        "Enter text to summarize",
        height=200,
        placeholder="Paste your long text here...",
        help="Enter the text you want to summarize"
    )
    
    max_length = st.slider("Max Summary Length (words)", 50, 500, 150)
    
    if st.button("🚀 Summarize", type="primary", use_container_width=True):
        if not text or text.strip() == "":
            st.error("⚠️ Please enter some text to summarize")
            return
        
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/text/summarize",
                    data={"text": text.strip(), "max_length": max_length},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display cache source prominently
                    cache_source = result.get("cache_source", "model")
                    response_time = result.get("response_time_ms", 0)
                    
                    # Show result with clear cache indicator
                    if cache_source == "memcache":
                        st.success("✅ **Ultra-Fast! Loaded from Memcached** ⚡")
                        st.info(f"🚀 Response: {response_time:.2f}ms | 💾 Source: **L1 Cache (Memcached)** | Speed: **600× faster!**")
                    elif cache_source == "redis":
                        st.success("✅ **Fast! Loaded from Redis** 🚀")
                        st.info(f"⚡ Response: {response_time:.2f}ms | 💾 Source: **L2 Cache (Redis)** | Speed: **100× faster!**")
                    else:
                        st.success("✅ **Fresh AI Generated!** 🤖")
                        st.info(f"🧠 Response: {response_time:.2f}ms | 🤖 Source: **Groq AI Model (llama-3.1-8b-instant)**")
                        st.caption("💡 **Tip**: Try the same text again to see lightning-fast cache response!")
                    
                    st.markdown("---")
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("⏱️ Response Time", f"{response_time:.2f}ms")
                    with col2:
                        compression = result.get("compression_ratio", 0)
                        st.metric("📊 Compression", f"{compression}%")
                    with col3:
                        st.metric("💾 Cache Source", cache_source.upper())
                    
                    # Summary output
                    st.markdown("### 📄 Summary")
                    st.markdown(f'<div class="success-box" style="font-size: 1.1rem; padding: 1.5rem;">{result["summary"]}</div>', 
                              unsafe_allow_html=True)
                    
                    # Statistics
                    with st.expander("📊 Detailed Statistics"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Original Length**: {result['original_length']} chars")
                            st.write(f"**Original Words**: {result['original_words']} words")
                        with col2:
                            st.write(f"**Summary Length**: {result['summary_length']} chars")
                            st.write(f"**Summary Words**: {result['summary_words']} words")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API Error: {str(e)}")

def show_chat():
    """Chat interface"""
    st.subheader("💬 AI Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "cache_info" in message:
                st.caption(f"⚡ {message['cache_info']}")
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/text/chat",
                        data={"message": prompt},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result.get("response", result.get("output", {}).get("response", "No response"))
                        cache_source = result.get("cache_source", "model")
                        response_time = result.get("response_time_ms", 0)
                        
                        st.markdown(ai_response)
                        cache_info = f"Source: {cache_source.upper()} | Time: {response_time:.2f}ms"
                        st.caption(f"⚡ {cache_info}")
                        
                        # Save assistant message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": ai_response,
                            "cache_info": cache_info
                        })
                    else:
                        st.error(f"Error: {response.status_code}")
                
                except requests.exceptions.RequestException as e:
                    st.error(f"API Error: {str(e)}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

def show_sentiment():
    """Sentiment analysis interface"""
    st.subheader("😊 Sentiment Analysis")
    
    text = st.text_area(
        "Enter text to analyze",
        height=150,
        placeholder="Type or paste text here...",
        help="Analyze the sentiment/emotion of the text"
    )
    
    if st.button("🔍 Analyze Sentiment", type="primary"):
        if not text:
            st.error("Please enter some text")
            return
        
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/text/sentiment",
                    data={"text": text},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    sentiment = result.get("sentiment", result.get("output", {}).get("sentiment", "unknown"))
                    
                    # Display sentiment with emoji
                    sentiment_emoji = {
                        "positive": "😊 Positive",
                        "negative": "😢 Negative",
                        "neutral": "😐 Neutral"
                    }
                    
                    st.success("✅ Analysis Complete!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sentiment", sentiment_emoji.get(sentiment, sentiment))
                    with col2:
                        response_time = result.get("response_time_ms", 0)
                        st.metric("Response Time", f"{response_time:.2f}ms")
                    
                    # Cache info
                    cache_source = result.get("cache_source", "model")
                    st.info(f"⚡ Cache Source: {cache_source.upper()}")
                    
                else:
                    st.error(f"Error: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {str(e)}")

def show_translation():
    """Translation interface"""
    st.subheader("🌍 Text Translation")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text = st.text_area(
            "Enter text to translate",
            height=150,
            placeholder="Type text in any language...",
            help="Enter the text you want to translate"
        )
    
    with col2:
        target_language = st.selectbox(
            "Target Language",
            ["Spanish", "French", "German", "Italian", "Portuguese", 
             "Chinese", "Japanese", "Korean", "Russian", "Arabic"]
        )
    
    if st.button("🌐 Translate", type="primary"):
        if not text:
            st.error("Please enter text to translate")
            return
        
        with st.spinner(f"Translating to {target_language}..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/text/translate",
                    data={"text": text, "target_language": target_language},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Translation Complete!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original Text:**")
                        st.info(result.get("original_text", text))
                    
                    with col2:
                        st.markdown(f"**Translated to {target_language}:**")
                        st.success(result.get("translated_text", result.get("output", {}).get("translated_text", "Translation not available")))
                    
                    # Cache info
                    cache_source = result.get("cache_source", "model")
                    response_time = result.get("response_time_ms", 0)
                    st.caption(f"⚡ Source: {cache_source.upper()} | Time: {response_time:.2f}ms")
                    
                else:
                    st.error(f"Error: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {str(e)}")
