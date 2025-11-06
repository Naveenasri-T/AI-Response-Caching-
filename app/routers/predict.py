"""
General Prediction Router
Handles the main /predict endpoint supporting both text and image tasks
"""
from fastapi import APIRouter, HTTPException, status
import time
import logging

from app.schemas import PredictRequest, PredictResponse
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK)
async def predict(req: PredictRequest):
    """
    Main prediction endpoint supporting both text and image tasks.
    
    Supported text tasks: summarization, sentiment, translation, chat, qa
    Supported image tasks: image_classification, image_captioning
    
    Args:
        req: PredictRequest with task_type, input, and optional params
    
    Returns:
        PredictResponse with output, cache information, and performance metrics
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
