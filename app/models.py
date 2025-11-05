from sqlalchemy import Column, BigInteger, String, Boolean, Integer, Float, TIMESTAMP, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RequestLog(Base):
    """
    Logs all AI requests and responses.
    Uses JSONB for flexible input/output storage with efficient querying and indexing.
    """
    __tablename__ = "request_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Request metadata
    task_type = Column(String(100), nullable=False, index=True)  # text, image, embedding
    operation = Column(String(100), nullable=True)  # summarize, sentiment, translate, classify, caption
    model_name = Column(String(200), nullable=True)
    
    # Input and output stored as JSONB for flexible querying
    input_json = Column(JSONB, nullable=False)
    output_json = Column(JSONB, nullable=False)
    
    # Caching information
    cache_used = Column(Boolean, default=False, index=True)
    cache_source = Column(String(20), nullable=True)  # "memcached", "redis", "none"
    cache_key = Column(String(255), nullable=True)
    
    # Performance metrics
    response_time_ms = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_task_operation', 'task_type', 'operation'),
        Index('idx_cache_performance', 'cache_used', 'cache_source', 'response_time_ms'),
    )
