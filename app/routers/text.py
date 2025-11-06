"""
Text Processing Router
Handles text-based AI tasks: summarization, sentiment analysis, translation, chat
"""
from fastapi import APIRouter, HTTPException, Form
import time
import logging

from app.services.ai_service import ai_service
from app.services.cache_service import cache_service
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text", tags=["Text Processing"])


@router.post("/summarize")
async def summarize_text(
    text: str = Form(..., description="Text to summarize"),
    max_length: int = Form(100, description="Maximum length of summary")
):
    """
    Summarize text - simple form input.
    
    Args:
        text: The text to summarize
        max_length: Maximum length of the summary in words (default: 100)
    
    Returns:
        Dictionary with summary, word counts, compression ratio, and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/text/summarize" \\
             -F "text=Your long text here..." \\
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


@router.post("/sentiment")
async def analyze_sentiment(
    text: str = Form(..., description="Text to analyze sentiment")
):
    """
    Analyze sentiment of text.
    
    Args:
        text: The text to analyze for sentiment
    
    Returns:
        Dictionary with sentiment analysis results and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/text/sentiment" \\
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


@router.post("/translate")
async def translate_text(
    text: str = Form(..., description="Text to translate"),
    target_language: str = Form("Spanish", description="Target language")
):
    """
    Translate text to another language.
    
    Args:
        text: The text to translate
        target_language: Target language for translation (default: Spanish)
    
    Returns:
        Dictionary with translated text and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/text/translate" \\
             -F "text=Hello, how are you?" \\
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


@router.post("/chat")
async def chat(
    message: str = Form(..., description="Your message")
):
    """
    Chat with AI.
    
    Args:
        message: Your chat message
    
    Returns:
        Dictionary with AI response and cache information
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/text/chat" \\
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
