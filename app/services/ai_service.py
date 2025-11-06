import time
import logging
import requests
from typing import Dict, Any, Tuple
from io import BytesIO

from app.core.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)


class AIService:
    """
    Handles AI model calls for text and image tasks using Groq API.
    """
    
    def __init__(self):
        self.groq_api_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL
    
    def process_text_task(self, task_type: str, text: str, params: dict = None) -> Dict[str, Any]:
        """
        Process text tasks using Groq API.
        Supports: summarization, sentiment, translation, chat, qa
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        params = params or {}
        
        # Build prompt based on task type
        prompt = self._build_text_prompt(task_type, text, params)
        
        # Call Groq API
        try:
            response = self._call_groq_api(prompt, params)
            
            # Format response based on task type
            output = self._format_text_response(task_type, response, text)
            return output
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def process_image_task(self, task_type: str, image_source: str, params: dict = None) -> Dict[str, Any]:
        """
        Process image tasks using Groq Vision API (Llama 4 Scout).
        Supports: image_classification, image_captioning
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        params = params or {}
        
        try:
            # Import Groq vision functions
            from app.services.groq_vision_service import classify_image_groq, caption_image_groq
            
            # Download image
            image_data = self._download_image(image_source)
            
            # Call appropriate Groq vision function
            if task_type == "image_classification":
                output = classify_image_groq(image_data)
            elif task_type == "image_captioning":
                output = caption_image_groq(image_data)
            else:
                raise ValueError(f"Unsupported image task: {task_type}")
            
            return output
            
        except Exception as e:
            logger.error(f"Groq Vision API error: {e}")
            raise
    
    def process_image_bytes(self, task_type: str, image_bytes: bytes, params: dict = None) -> Dict[str, Any]:
        """
        Process image tasks using Groq Vision API (Llama 4 Scout) with image bytes directly.
        Supports: image_classification, image_captioning
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        params = params or {}
        
        try:
            # Import Groq vision functions
            from app.services.groq_vision_service import classify_image_groq, caption_image_groq
            
            # Call appropriate Groq vision function directly with bytes
            if task_type == "image_classification":
                output = classify_image_groq(image_bytes)
            elif task_type == "image_captioning":
                output = caption_image_groq(image_bytes)
            else:
                raise ValueError(f"Unsupported image task: {task_type}")
            
            return output
            
        except Exception as e:
            logger.error(f"Groq Vision API error: {e}")
            raise
    
    def _build_text_prompt(self, task_type: str, text: str, params: dict) -> str:
        """
        Build appropriate prompt for each task type.
        """
        if task_type == "summarization":
            max_length = params.get("max_length", 100)
            return f"""You are a text summarization assistant. Your task is to create a SHORTER, CONDENSED summary.

CRITICAL RULES:
- The summary MUST be shorter than the original text
- Maximum length: {max_length} words
- Be concise and capture only the key points
- Do not add explanations or extra details
- Just provide the summary, nothing else

Original text ({len(text.split())} words):
{text}

Provide a summary in {max_length} words or less:"""
        
        elif task_type == "sentiment":
            return f"Analyze the sentiment of the following text. Respond with only: positive, negative, or neutral.\n\nText: {text}\n\nSentiment:"
        
        elif task_type == "translation":
            target_lang = params.get("target_language", "Spanish")
            return f"Translate the following text to {target_lang}:\n\n{text}\n\nTranslation:"
        
        elif task_type == "chat":
            return text
        
        elif task_type == "qa":
            context = params.get("context", "")
            return f"Context: {context}\n\nQuestion: {text}\n\nAnswer:"
        
        else:
            return text
    
    def _call_groq_api(self, prompt: str, params: dict) -> str:
        """
        Call Groq API for text generation.
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": params.get("model", self.groq_model),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 1000)
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Check for errors and log detailed message
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"Groq API error: {response.status_code} - {error_detail}")
            response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    def _format_text_response(self, task_type: str, response: str, original_text: str) -> Dict[str, Any]:
        """
        Format API response based on task type.
        """
        if task_type == "summarization":
            # Trim response if it's too long (shouldn't happen but just in case)
            response = response.strip()
            original_word_count = len(original_text.split())
            summary_word_count = len(response.split())
            
            return {
                "summary": response,
                "original_length": len(original_text),
                "summary_length": len(response),
                "original_words": original_word_count,
                "summary_words": summary_word_count,
                "compression_ratio": round((1 - summary_word_count / original_word_count) * 100, 1) if original_word_count > 0 else 0
            }
        
        elif task_type == "sentiment":
            sentiment = response.lower().strip()
            # Extract first word if response is longer
            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = sentiment.split()[0] if sentiment else "neutral"
            return {"sentiment": sentiment, "text": original_text}
        
        elif task_type == "translation":
            return {"translated_text": response, "original_text": original_text}
        
        elif task_type in ["chat", "qa"]:
            return {"response": response, "input": original_text}
        
        else:
            return {"result": response}
    
    def _download_image(self, image_source: str) -> bytes:
        """
        Download image from URL.
        """
        if image_source.startswith("http"):
            response = requests.get(image_source, timeout=15)
            response.raise_for_status()
            return response.content
        else:
            raise ValueError("Only HTTP/HTTPS image URLs are supported")


# Global AI service instance
ai_service = AIService()
