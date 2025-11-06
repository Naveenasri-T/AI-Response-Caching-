"""
Image Processing Page
"""
import streamlit as st
import requests
from PIL import Image
import io
import base64

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def show():
    """Display image processing interface"""
    
    st.header("🖼️ Image Processing with Groq Vision")
    
    # Task selection
    task = st.selectbox(
        "Select Task",
        ["Image Captioning", "Image Classification"],
        help="Choose the image processing task"
    )
    
    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["📤 Upload Image", "🔗 Image URL"],
        horizontal=True
    )
    
    image_data = None
    image_display = None
    
    # Handle input method
    if input_method == "📤 Upload Image":
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"],
            help="Upload an image file (PNG, JPG, JPEG)"
        )
        
        if uploaded_file:
            image_data = uploaded_file.getvalue()
            image_display = Image.open(io.BytesIO(image_data))
    
    else:  # Image URL
        image_url = st.text_input(
            "Enter image URL",
            placeholder="https://example.com/image.jpg",
            help="Provide a direct URL to an image"
        )
        
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    image_data = response.content
                    image_display = Image.open(io.BytesIO(image_data))
                else:
                    st.error(f"Failed to fetch image: {response.status_code}")
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
    
    # Display image preview
    if image_display:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image_display, caption="Preview", use_container_width=True)
    
    # Process button
    if st.button(f"🚀 Process Image", type="primary", disabled=not image_data):
        if task == "Image Captioning":
            process_caption(image_data, input_method == "🔗 Image URL", 
                          image_url if input_method == "🔗 Image URL" else None)
        else:
            process_classification(image_data, input_method == "🔗 Image URL",
                                 image_url if input_method == "🔗 Image URL" else None)

def process_caption(image_data, is_url, image_url=None):
    """Process image captioning"""
    with st.spinner("Generating caption..."):
        try:
            if is_url:
                # Use URL endpoint with form data
                response = requests.post(
                    f"{API_BASE_URL}/image/caption",
                    data={"image_url": image_url},
                    timeout=30
                )
            else:
                # Use upload endpoint
                files = {"image": ("image.jpg", image_data, "image/jpeg")}
                response = requests.post(
                    f"{API_BASE_URL}/image/upload/caption",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ Caption Generated!")
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    cache_source = result.get("cache_source", "model")
                    st.metric("Cache Source", cache_source.upper())
                with col2:
                    response_time = result.get("response_time_ms", 0)
                    st.metric("Response Time", f"{response_time:.2f}ms")
                with col3:
                    st.metric("Model", "Llama 4 Scout")
                
                # Display caption
                st.markdown("### 📝 Generated Caption")
                caption_text = result.get("caption", result.get("output", {}).get("caption", "No caption available"))
                st.markdown(f'<div class="success-box" style="font-size: 1.2rem;">{caption_text}</div>', 
                          unsafe_allow_html=True)
                
                # Cache performance info
                if cache_source != "model":
                    st.balloons()
                    st.success("🎉 This was a cached response - Lightning fast!")
                else:
                    st.info("💡 Try the same image again to see caching in action!")
            
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")

def process_classification(image_data, is_url, image_url=None):
    """Process image classification"""
    with st.spinner("Classifying image..."):
        try:
            if is_url:
                # Use URL endpoint with form data
                response = requests.post(
                    f"{API_BASE_URL}/image/classify",
                    data={"image_url": image_url},
                    timeout=30
                )
            else:
                # Use upload endpoint
                files = {"image": ("image.jpg", image_data, "image/jpeg")}
                response = requests.post(
                    f"{API_BASE_URL}/image/upload/classify",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ Classification Complete!")
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    cache_source = result.get("cache_source", "model")
                    st.metric("Cache Source", cache_source.upper())
                with col2:
                    response_time = result.get("response_time_ms", 0)
                    st.metric("Response Time", f"{response_time:.2f}ms")
                with col3:
                    st.metric("Model", "Llama 4 Scout")
                
                # Display predictions
                st.markdown("### 🏷️ Classification Results")
                
                predictions = result.get("predictions", result.get("output", {}).get("predictions", []))
                
                for i, pred in enumerate(predictions[:5], 1):
                    label = pred.get("label", "Unknown")
                    score = pred.get("score", 0)
                    
                    # Progress bar for confidence
                    st.markdown(f"**{i}. {label}**")
                    st.progress(score)
                    st.caption(f"Confidence: {score*100:.2f}%")
                
                # Cache performance info
                if cache_source != "model":
                    st.balloons()
                    st.success("🎉 This was a cached response - Lightning fast!")
                else:
                    st.info("💡 Try the same image again to see caching in action!")
            
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")

    st.markdown("---")
    st.info("**Powered by**: Groq Llama 4 Scout Vision Model (17B parameters)")
