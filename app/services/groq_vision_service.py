"""
Groq Vision Service
Uses Groq's Llama 4 vision models for image processing (classification and captioning)
No PyTorch dependencies needed!
"""
from groq import Groq
from typing import Dict, Any
import logging
import base64
from app.core.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Use Llama 4 Scout (current model as of Nov 2025)
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def classify_image_groq(image_data: bytes) -> Dict[str, Any]:
    """
    Classify image using Groq's vision model
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dict containing classification results
    """
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Call Groq vision model (Llama 4 Scout)
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Classify this image. Provide the top 5 most likely categories with confidence scores. Format as: category: score (e.g., 'cat: 0.95')"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_completion_tokens=300
        )
        
        # Parse response
        result_text = response.choices[0].message.content
        
        # Extract predictions from text
        predictions = []
        lines = result_text.strip().split('\n')
        for line in lines[:5]:  # Top 5
            line = line.strip()
            if ':' in line:
                # Remove numbering like "1.", "2.", etc.
                line = line.split('.', 1)[-1].strip()
                parts = line.split(':')
                if len(parts) >= 2:
                    label = parts[0].strip()
                    try:
                        score_text = parts[1].strip().split()[0]  # Get first number
                        score = float(score_text)
                    except:
                        score = 0.5  # Default score if parsing fails
                    predictions.append({"label": label, "score": score})
        
        # If parsing failed, return raw text
        if not predictions:
            predictions = [{"label": result_text[:100], "score": 1.0}]
        
        return {
            "predictions": predictions,
            "model_used": VISION_MODEL
        }
        
    except Exception as e:
        logger.error(f"Groq image classification error: {e}", exc_info=True)
        raise Exception(f"Image classification failed: {str(e)}")


def caption_image_groq(image_data: bytes) -> Dict[str, Any]:
    """
    Generate caption for image using Groq's vision model
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dict containing caption
    """
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Call Groq vision model (Llama 4 Scout)
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this image in one clear, concise sentence."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.5,
            max_completion_tokens=100
        )
        
        # Get caption from response
        caption = response.choices[0].message.content.strip()
        
        return {
            "caption": caption,
            "model_used": VISION_MODEL
        }
        
    except Exception as e:
        logger.error(f"Groq image captioning error: {e}", exc_info=True)
        raise Exception(f"Image captioning failed: {str(e)}")
