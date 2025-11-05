# 🚀 Setup and Deployment Guide

Complete guide to set up and run the AI Response Caching POC.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Docker Desktop** (Windows/Mac) or Docker + Docker Compose (Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker-compose --version`

- **API Keys**
  - **Groq API Key**: https://console.groq.com (free tier available)
  - **HuggingFace Token**: https://huggingface.co/settings/tokens (free)

### Optional (for local development without Docker)

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Memcached 1.6+

---

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd AI-Response-Caching-
```

### Step 2: Configure Environment

Edit the `.env` file with your API keys:

```bash
# Required: Add your API keys
GROQ_API_KEY=your_groq_key_here
HF_API_KEY=your_huggingface_token_here

# Database (choose one):
# Option 1: Use Neon DB (cloud) - already configured
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_FzHjrtqx08QO@ep-shy-union-adlto399-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

# Option 2: Use local Docker Postgres (uncomment this and comment above)
# DATABASE_URL=postgresql+asyncpg://goml:goml_pass@localhost:5432/goml_db

# Cache settings (defaults are fine)
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600
MEMCACHE_HOST=localhost
MEMCACHE_PORT=11211
MEMCACHE_TTL=300
```

---

## Configuration

### Environment Variables Explained

| Variable | Purpose | Default |
|----------|---------|---------|
| `GROQ_API_KEY` | Groq API authentication | *Required* |
| `HF_API_KEY` | HuggingFace authentication | *Required* |
| `GROQ_MODEL` | Groq model to use | `llama3-8b-8192` |
| `DATABASE_URL` | PostgreSQL connection | Neon DB URL |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `REDIS_TTL` | L2 cache TTL (seconds) | `3600` (1 hour) |
| `MEMCACHE_HOST` | Memcached host | `localhost` |
| `MEMCACHE_PORT` | Memcached port | `11211` |
| `MEMCACHE_TTL` | L1 cache TTL (seconds) | `300` (5 min) |
| `DEBUG` | Enable debug logging | `false` |

### Cache TTL Strategy

- **Memcached (L1)**: 300 seconds (5 minutes)
  - For very recent, frequently repeated requests
  - Ultra-fast response (~1-3ms)

- **Redis (L2)**: 3600 seconds (1 hour)
  - For active requests in current session
  - Fast response (~5-10ms)

Adjust these based on your use case:
- Higher traffic → Lower TTLs
- Lower traffic → Higher TTLs

---

## Running the Application

### Method 1: Docker Compose (Recommended)

**Windows:**
```bash
# Double-click start.bat
# OR run in terminal:
docker-compose up --build
```

**Mac/Linux:**
```bash
chmod +x start.sh  # if you create start.sh
docker-compose up --build
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- Memcached on port 11211
- FastAPI app on port 8000

### Method 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start services (if not using Docker)
# - Start PostgreSQL, Redis, Memcached manually
# - Or use: docker-compose up postgres redis memcached

# Run the application
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Installation

1. **Check health**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **View API docs**:
   Open http://localhost:8000/docs in browser

3. **Run test suite**:
   ```bash
   python test_api.py
   ```

---

## Testing

### Automated Tests

```bash
python test_api.py
```

This tests:
- Health check
- Text summarization (with cache verification)
- Sentiment analysis
- Image captioning
- Statistics endpoint

### Manual Testing

#### Test Summarization

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "summarization",
    "input": "Artificial intelligence is transforming industries worldwide...",
    "params": {"max_length": 50}
  }'
```

#### Test Cache Hit

Run the same request twice. Second request should be much faster with `"cache_source": "memcached"`.

#### View Statistics

```bash
curl http://localhost:8000/api/v1/statistics?days=7
```

---

## Production Deployment

### Docker Production Build

```dockerfile
# Build optimized image
docker build -t ai-cache-poc:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ai-cache-app \
  ai-cache-poc:latest
```

### Kubernetes Deployment

```yaml
# Example kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-cache-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-cache-api
  template:
    metadata:
      labels:
        app: ai-cache-api
    spec:
      containers:
      - name: api
        image: ai-cache-poc:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: groq-key
```

### Production Checklist

- [ ] Use managed PostgreSQL (Neon, AWS RDS, etc.)
- [ ] Use managed Redis (AWS ElastiCache, Redis Cloud, etc.)
- [ ] Set `DEBUG=false` in production
- [ ] Add authentication/API keys
- [ ] Configure CORS properly
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation
- [ ] Set up SSL/TLS (use nginx/traefik)
- [ ] Implement rate limiting
- [ ] Set up health check monitoring
- [ ] Configure automatic backups

---

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Solution**: Start Docker Desktop

```bash
# Windows: Start Docker Desktop app
# Linux: sudo systemctl start docker
```

### Issue: "Port 8000 already in use"

**Solution**: Stop other services or change port

```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Kill the process or change port in docker-compose.yml
```

### Issue: "Database connection failed"

**Solutions**:

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps
   ```

2. Verify DATABASE_URL in `.env`

3. Check logs:
   ```bash
   docker-compose logs postgres
   ```

### Issue: "GROQ_API_KEY not configured"

**Solution**: Add your Groq API key to `.env`:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

### Issue: "Redis connection failed"

**Solutions**:

1. Check Redis is running:
   ```bash
   docker-compose ps redis
   ```

2. Test Redis connection:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Issue: Cache not working

**Debug steps**:

1. Check health endpoint:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. Verify cache services are up:
   ```bash
   docker-compose ps
   ```

3. Check logs:
   ```bash
   docker-compose logs app
   ```

### Issue: Slow responses even with cache

**Solutions**:

1. Check cache hit rate:
   ```bash
   curl http://localhost:8000/api/v1/statistics
   ```

2. Verify network latency to cache services

3. Check if TTLs are too short (increase in `.env`)

---

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f redis
docker-compose logs -f postgres
```

### Check Resource Usage

```bash
docker stats
```

### Database Queries

```bash
# Connect to database
docker-compose exec postgres psql -U goml -d goml_db

# View recent requests
SELECT task_type, cache_source, response_time_ms, created_at 
FROM request_logs 
ORDER BY created_at DESC 
LIMIT 10;

# Cache hit rate
SELECT 
  cache_source,
  COUNT(*) as count,
  AVG(response_time_ms) as avg_time
FROM request_logs 
GROUP BY cache_source;
```

---

## Performance Tips

1. **Warm Up Cache**: Run common queries after deployment
2. **Monitor Hit Rate**: Aim for >60% cache hit rate
3. **Tune TTLs**: Based on your traffic patterns
4. **Scale Horizontally**: Add more app instances behind load balancer
5. **Use Redis Cluster**: For high-traffic scenarios
6. **Optimize Database**: Add indexes for common queries

---

## Support

For issues or questions:
- Check logs: `docker-compose logs app`
- Run tests: `python test_api.py`
- Open an issue on GitHub

---

**Happy Caching! 🚀**
