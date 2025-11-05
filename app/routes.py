from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
import time
import logging
import base64
from pathlib import Path

from app.schemas import PredictRequest, PredictResponse, HealthCheck, CacheStatistics
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service
from app.services.db_service import db_service
from app.config import HF_IMAGE_CLASSIFICATION_MODEL, HF_IMAGE_CAPTIONING_MODEL

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK)
async def predict(req: PredictRequest):
    """
    Main prediction endpoint supporting both text and image tasks.
    
    Supported text tasks: summarization, sentiment, translation, chat, qa
    Supported image tasks: image_classification, image_captioning
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not req.task_type or req.input is None:
            raise HTTPException(
                status_code=400,
                detail="task_type and input are required"
            )
        
        # Generate cache key
        cache_key = cache_service.generate_cache_key(
            req.task_type,
            req.input,
            req.params
        )
        
        # Check cache (L1: Memcached, L2: Redis)
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            # Cache hit!
            response_time_ms = (time.time() - start_time) * 1000
            
            # Log to database
            await db_service.log_request(
                task_type=req.task_type,
                operation=req.params.get("operation") if req.params else None,
                model_name=cached_result.get("model", req.model or "cached"),
                input_json={"input": req.input, "params": req.params},
                output_json=cached_result,
                cache_used=True,
                cache_source=cache_source,
                cache_key=cache_key,
                response_time_ms=response_time_ms
            )
            
            return PredictResponse(
                output=cached_result,
                cache_source=cache_source,
                response_time_ms=response_time_ms,
                model_name=cached_result.get("model", req.model or "cached"),
                task_type=req.task_type,
                cache_key=cache_key
            )
        
        # Cache miss - call AI model
        logger.info(f"Cache miss for task: {req.task_type}")
        
        # Determine if text or image task
        is_image_task = req.task_type in ["image_classification", "image_captioning"]
        
        if is_image_task:
            # Extract image source
            if isinstance(req.input, dict):
                image_source = req.input.get("image_url") or req.input.get("url")
            else:
                image_source = req.input
            
            if not image_source:
                raise HTTPException(
                    status_code=400,
                    detail="Image URL required for image tasks"
                )
            
            output = ai_service.process_image_task(
                req.task_type,
                image_source,
                req.params
            )
        else:
            # Text task
            if isinstance(req.input, dict):
                text = req.input.get("text") or req.input.get("prompt")
            else:
                text = str(req.input)
            
            if not text:
                raise HTTPException(
                    status_code=400,
                    detail="Text input required for text tasks"
                )
            
            output = ai_service.process_text_task(
                req.task_type,
                text,
                req.params
            )
        
        model_name = req.model or output.get("model", "default")
        response_time_ms = (time.time() - start_time) * 1000
        
        # Store in cache
        cache_service.set_in_cache(cache_key, output)
        
        # Log to database
        await db_service.log_request(
            task_type=req.task_type,
            operation=req.params.get("operation") if req.params else None,
            model_name=model_name,
            input_json={"input": req.input, "params": req.params},
            output_json=output,
            cache_used=False,
            cache_source="model",
            cache_key=cache_key,
            response_time_ms=response_time_ms
        )
        
        return PredictResponse(
            output=output,
            cache_source="model",
            response_time_ms=response_time_ms,
            model_name=model_name,
            task_type=req.task_type,
            cache_key=cache_key
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    redis_ok, memcached_ok = cache_service.health_check()
    database_ok = await db_service.health_check()
    
    overall_status = "healthy" if (redis_ok and memcached_ok and database_ok) else "degraded"
    
    return HealthCheck(
        status=overall_status,
        redis_connected=redis_ok,
        memcached_connected=memcached_ok,
        database_connected=database_ok
    )


@router.get("/statistics", response_model=CacheStatistics)
async def get_statistics(days: int = 7):
    """
    Get cache performance statistics for the last N days.
    """
    try:
        stats = await db_service.get_statistics(days)
        
        return CacheStatistics(
            total_requests=stats["total_requests"],
            cache_hits=stats["cache_hits"],
            cache_misses=stats["cache_misses"],
            memcached_hits=stats["memcached_hits"],
            redis_hits=stats["redis_hits"],
            average_response_time_ms=stats["average_response_time_ms"],
            cache_hit_rate=stats["cache_hit_rate"],
            time_period=f"last_{days}_days"
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )


# ============================================================================
# USER-FRIENDLY ENDPOINTS - Easy to use with forms and file uploads
# ============================================================================

@router.post("/text/summarize")
async def summarize_text(
    text: str = Form(..., description="Text to summarize"),
    max_length: int = Form(100, description="Maximum length of summary")
):
    """
    Summarize text - simple form input.
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/text/summarize" \
         -F "text=Your long text here..." \
         -F "max_length=50"
    """
    start_time = time.time()
    
    try:
        # Generate cache key
        cache_key = cache_service.generate_cache_key(
            "summarization",
            text,
            {"max_length": max_length}
        )
        
        # Check cache
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="summarization",
                operation="summarize",
                model_name="llama-3.1-8b-instant",
                input_json={"text": text, "max_length": max_length},
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
        
        # Call AI
        output = ai_service.process_text_task("summarization", text, {"max_length": max_length})
        response_time_ms = (time.time() - start_time) * 1000
        
        # Cache and log
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="summarization",
            operation="summarize",
            model_name="llama-3.1-8b-instant",
            input_json={"text": text, "max_length": max_length},
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
        logger.error(f"Summarization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/sentiment")
async def analyze_sentiment(
    text: str = Form(..., description="Text to analyze sentiment")
):
    """
    Analyze sentiment of text.
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/text/sentiment" \
         -F "text=I love this product!"
    """
    start_time = time.time()
    
    try:
        cache_key = cache_service.generate_cache_key("sentiment", text, {})
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="sentiment",
                operation="analyze",
                model_name="llama-3.1-8b-instant",
                input_json={"text": text},
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
        
        output = ai_service.process_text_task("sentiment", text, {})
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="sentiment",
            operation="analyze",
            model_name="llama-3.1-8b-instant",
            input_json={"text": text},
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
        logger.error(f"Sentiment analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/translate")
async def translate_text(
    text: str = Form(..., description="Text to translate"),
    target_language: str = Form("Spanish", description="Target language")
):
    """
    Translate text to another language.
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/text/translate" \
         -F "text=Hello, how are you?" \
         -F "target_language=Spanish"
    """
    start_time = time.time()
    
    try:
        params = {"target_language": target_language}
        cache_key = cache_service.generate_cache_key("translation", text, params)
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="translation",
                operation="translate",
                model_name="llama-3.1-8b-instant",
                input_json={"text": text, "target_language": target_language},
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
        
        output = ai_service.process_text_task("translation", text, params)
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="translation",
            operation="translate",
            model_name="llama-3.1-8b-instant",
            input_json={"text": text, "target_language": target_language},
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
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/chat")
async def chat(
    message: str = Form(..., description="Your message")
):
    """
    Chat with AI.
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/text/chat" \
         -F "message=What is the capital of France?"
    """
    start_time = time.time()
    
    try:
        cache_key = cache_service.generate_cache_key("chat", message, {})
        cached_result, cache_source = cache_service.get_from_cache(cache_key)
        
        if cached_result:
            response_time_ms = (time.time() - start_time) * 1000
            await db_service.log_request(
                task_type="chat",
                operation="chat",
                model_name="llama-3.1-8b-instant",
                input_json={"message": message},
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
        
        output = ai_service.process_text_task("chat", message, {})
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="chat",
            operation="chat",
            model_name="llama-3.1-8b-instant",
            input_json={"message": message},
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
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/upload/caption")
async def caption_uploaded_image(
    image: UploadFile = File(..., description="Image file to caption")
):
    """
    Upload an image file and get a caption.
    
    Supports: JPG, JPEG, PNG, GIF, BMP, WEBP
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/image/upload/caption" \
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
                model_name="Salesforce/blip-image-captioning-large",
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
        
        # Process with HuggingFace using bytes directly
        output = ai_service.process_image_bytes("image_captioning", image_bytes, {})
        response_time_ms = (time.time() - start_time) * 1000
        
        # Cache and log
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_captioning",
            operation="caption_upload",
            model_name="Salesforce/blip-image-captioning-large",
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


@router.post("/image/caption")
async def caption_image_url(
    image_url: str = Form(..., description="URL of the image to caption")
):
    """
    Get caption for an image from URL.
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/image/caption" \
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
                model_name="Salesforce/blip-image-captioning-large",
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
        
        output = ai_service.process_image_task("image_captioning", image_url, {})
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_captioning",
            operation="caption",
            model_name="Salesforce/blip-image-captioning-large",
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


@router.post("/image/classify")
async def classify_image_url(
    image_url: str = Form(..., description="URL of the image to classify"),
    top_k: int = Form(5, description="Number of top predictions to return")
):
    """
    Classify an image from URL.
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/image/classify" \
         -F "image_url=https://example.com/image.jpg" \
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
                model_name=HF_IMAGE_CLASSIFICATION_MODEL,
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
        
        output = ai_service.process_image_task("image_classification", image_url, params)
        response_time_ms = (time.time() - start_time) * 1000
        
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_classification",
            operation="classify",
            model_name=HF_IMAGE_CLASSIFICATION_MODEL,
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


@router.post("/image/upload/classify")
async def classify_uploaded_image(
    image: UploadFile = File(..., description="Image file to classify"),
    top_k: int = Form(5, description="Number of top predictions to return")
):
    """
    Upload an image file and classify it.
    
    Supports: JPG, JPEG, PNG, GIF, BMP, WEBP
    
    Usage with curl:
    curl -X POST "http://localhost:8000/api/v1/image/upload/classify" \
         -F "image=@/path/to/your/image.jpg" \
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
                model_name=HF_IMAGE_CLASSIFICATION_MODEL,
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
        
        # Process with HuggingFace using bytes directly
        output = ai_service.process_image_bytes("image_classification", image_bytes, {"top_k": top_k})
        response_time_ms = (time.time() - start_time) * 1000
        
        # Cache and log
        cache_service.set_in_cache(cache_key, output)
        await db_service.log_request(
            task_type="image_classification",
            operation="classify_upload",
            model_name=HF_IMAGE_CLASSIFICATION_MODEL,
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
