from pydantic import BaseModel, HttpUrl, Field
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


# Enums for task types
class TaskType(str, Enum):
    SUMMARIZATION = "summarization"
    SENTIMENT = "sentiment"
    CLASSIFICATION = "classification"
    TRANSLATION = "translation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE_CLASSIFICATION = "image_classification"
    IMAGE_CAPTIONING = "image_captioning"


class PredictRequest(BaseModel):
    task_type: str = Field(..., description="Type of AI task to perform")
    model: Optional[str] = Field(None, description="Optional model override (Groq model or HF model id)")
    input: Any = Field(..., description="Input data: text string, image URL, or structured payload")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters for the model")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "task_type": "summarization",
                    "input": "Long text to summarize...",
                    "params": {"max_length": 100}
                },
                {
                    "task_type": "sentiment",
                    "input": "I love this product!",
                    "params": {}
                },
                {
                    "task_type": "image_captioning",
                    "input": "https://example.com/image.jpg",
                    "params": {}
                }
            ]
        }


class PredictResponse(BaseModel):
    output: Any = Field(..., description="AI model output")
    cache_source: str = Field(..., description="Cache source: 'memcached', 'redis', or 'model' (no cache)")
    response_time_ms: float = Field(..., description="Total response time in milliseconds")
    model_name: Optional[str] = Field(None, description="Name of the model used")
    task_type: Optional[str] = Field(None, description="Task type that was executed")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Response timestamp")
    cache_key: Optional[str] = Field(None, description="Cache key used for this request")
    
    class Config:
        json_schema_extra = {
            "example": {
                "output": {"summary": "This is a summary of the text."},
                "cache_source": "memcached",
                "response_time_ms": 15.5,
                "model_name": "llama3-8b-8192",
                "task_type": "summarization",
                "timestamp": "2025-11-03T10:00:00Z"
            }
        }


# Health Check Schema
class HealthCheck(BaseModel):
    status: str = "healthy"
    redis_connected: bool
    memcached_connected: bool
    database_connected: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Statistics Schema
class CacheStatistics(BaseModel):
    total_requests: int
    cache_hits: int
    cache_misses: int
    memcached_hits: int
    redis_hits: int
    average_response_time_ms: float
    cache_hit_rate: float
    time_period: str = "all_time"
