"""
Image Processing Router
Handles image-based AI tasks: classification and captioning with URL and file upload support
Uses Groq's Llama 4 Scout vision model - same API as text processing!
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import time
import logging
import base64
import requests
from io import BytesIO

from app.services.groq_vision_service import classify_image_groq, caption_image_groq, VISION_MODEL
from app.services.cache_service import cache_service
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/image", tags=["Image Processing"])


@router.post("/upload/caption")
async def caption_uploaded_image(
    image: UploadFile = File(..., description="Image file to caption")
):
    """
    Upload an image file and get a caption.
    
    Supports: JPG, JPEG, PNG, GIF, BMP, WEBP
    
    Args:
        image: Image file to caption
    
    Returns:
        Dictionary with image caption, file info, and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/image/upload/caption" \\
             -F "image=@/path/to/your/image.jpg"
    """
    start_time = time.time()
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read image bytes
        image_bytes = await image.read()
        
        # Convert to base64 for caching key (use first 100 chars to avoid huge keys)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        cache_key = cache_service.generate_cache_key("image_captioning", image_b64[:100], {"filename": image.filename})
        
        # Check cache
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="image_captioning",
                operation="caption_upload",
                model_name=VISION_MODEL,
                input_json={"filename": image.filename, "size_bytes": len(image_bytes), "content_type": image.content_type},
                output_json=cached_result,
                cache_used=True,
                cache_source=cache_source,
                cache_key=cache_key,
                response_time_ms=response_time_ms
            )
            return {
                **cached_result,
                "filename": image.filename,
                "size_bytes": len(image_bytes),
                "cache_hit": True,
                "cache_source": cache_source,
                "response_time_ms": response_time_ms
            }
        
        # Process with Groq vision model
        output = caption_image_groq(image_bytes)
        response_time_ms = (time.time() - start_time) * 1000
        
        # Cache and log
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_captioning",
            operation="caption_upload",
            model_name=VISION_MODEL,
            input_json={"filename": image.filename, "size_bytes": len(image_bytes), "content_type": image.content_type},
            output_json=output,
            cache_used=False,
            cache_source="model",
            cache_key=cache_key,
            response_time_ms=response_time_ms
        )
        
        return {
            **output,
            "filename": image.filename,
            "size_bytes": len(image_bytes),
            "cache_hit": False,
            "cache_source": "model",
            "response_time_ms": response_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image caption upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/caption")
async def caption_image_url(
    image_url: str = Form(..., description="URL of the image to caption")
):
    """
    Get caption for an image from URL.
    
    Args:
        image_url: URL of the image to caption
    
    Returns:
        Dictionary with image caption and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/image/caption" \\
             -F "image_url=https://example.com/image.jpg"
    """
    start_time = time.time()
    
    try:
        cache_key = cache_service.generate_cache_key("image_captioning", image_url, {})
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="image_captioning",
                operation="caption",
                model_name=VISION_MODEL,
                input_json={"image_url": image_url},
                output_json=cached_result,
                cache_used=True,
                cache_source=cache_source,
                cache_key=cache_key,
                response_time_ms=response_time_ms
            )
            return {
                **cached_result,
                "cache_hit": True,
                "cache_source": cache_source,
                "response_time_ms": response_time_ms
            }
        
        # Download image from URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_bytes = response.content
        
        # Process with Groq vision model
        output = caption_image_groq(image_bytes)
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_captioning",
            operation="caption",
            model_name=VISION_MODEL,
            input_json={"image_url": image_url},
            output_json=output,
            cache_used=False,
            cache_source="model",
            cache_key=cache_key,
            response_time_ms=response_time_ms
        )
        
        return {
            **output,
            "cache_hit": False,
            "cache_source": "model",
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        logger.error(f"Image caption error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify")
async def classify_image_url(
    image_url: str = Form(..., description="URL of the image to classify"),
    top_k: int = Form(5, description="Number of top predictions to return")
):
    """
    Classify an image from URL.
    
    Args:
        image_url: URL of the image to classify
        top_k: Number of top predictions to return (default: 5)
    
    Returns:
        Dictionary with classification results and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/image/classify" \\
             -F "image_url=https://example.com/image.jpg" \\
             -F "top_k=5"
    """
    start_time = time.time()
    
    try:
        params = {"top_k": top_k}
        cache_key = cache_service.generate_cache_key("image_classification", image_url, params)
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="image_classification",
                operation="classify",
                model_name=VISION_MODEL,
                input_json={"image_url": image_url, "top_k": top_k},
                output_json=cached_result,
                cache_used=True,
                cache_source=cache_source,
                cache_key=cache_key,
                response_time_ms=response_time_ms
            )
            return {
                **cached_result,
                "cache_hit": True,
                "cache_source": cache_source,
                "response_time_ms": response_time_ms
            }
        
        # Download image from URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_bytes = response.content
        
        # Process with Groq vision model
        output = classify_image_groq(image_bytes)
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_classification",
            operation="classify",
            model_name=VISION_MODEL,
            input_json={"image_url": image_url, "top_k": top_k},
            output_json=output,
            cache_used=False,
            cache_source="model",
            cache_key=cache_key,
            response_time_ms=response_time_ms
        )
        
        return {
            **output,
            "cache_hit": False,
            "cache_source": "model",
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        logger.error(f"Image classification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/classify")
async def classify_uploaded_image(
    image: UploadFile = File(..., description="Image file to classify"),
    top_k: int = Form(5, description="Number of top predictions to return")
):
    """
    Upload an image file and classify it.
    
    Supports: JPG, JPEG, PNG, GIF, BMP, WEBP
    
    Args:
        image: Image file to classify
        top_k: Number of top predictions to return (default: 5)
    
    Returns:
        Dictionary with classification results, file info, and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/image/upload/classify" \\
             -F "image=@/path/to/your/image.jpg" \\
             -F "top_k=5"
    """
    start_time = time.time()
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read image bytes
        image_bytes = await image.read()
        
        # Convert to base64 for caching key (use first 100 chars to avoid huge keys)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        params = {"top_k": top_k, "filename": image.filename}
        cache_key = cache_service.generate_cache_key("image_classification", image_b64[:100], params)
        
        # Check cache
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="image_classification",
                operation="classify_upload",
                model_name=VISION_MODEL,
                input_json={"filename": image.filename, "size_bytes": len(image_bytes), "content_type": image.content_type, "top_k": top_k},
                output_json=cached_result,
                cache_used=True,
                cache_source=cache_source,
                cache_key=cache_key,
                response_time_ms=response_time_ms
            )
            return {
                **cached_result,
                "filename": image.filename,
                "size_bytes": len(image_bytes),
                "cache_hit": True,
                "cache_source": cache_source,
                "response_time_ms": response_time_ms
            }
        
        # Process with Groq vision model
        output = classify_image_groq(image_bytes)
        response_time_ms = (time.time() - start_time) * 1000
        
        # Cache and log
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_classification",
            operation="classify_upload",
            model_name=VISION_MODEL,
            input_json={"filename": image.filename, "size_bytes": len(image_bytes), "content_type": image.content_type, "top_k": top_k},
            output_json=output,
            cache_used=False,
            cache_source="model",
            cache_key=cache_key,
            response_time_ms=response_time_ms
        )
        
        return {
            **output,
            "filename": image.filename,
            "size_bytes": len(image_bytes),
            "cache_hit": False,
            "cache_source": "model",
            "response_time_ms": response_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image classification upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
