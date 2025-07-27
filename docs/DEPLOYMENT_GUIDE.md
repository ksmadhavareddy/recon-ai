# 🚀 Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying the AI Reconciliation System across different environments, from local development to production deployment.

## 🏠 Local Development Setup

### Prerequisites

```bash
# Ensure Python 3.8+ is installed
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, uvicorn, pandas, lightgbm; print('✅ All packages installed')"
```

### Quick Start

```bash
# 1. Start API Server
python api_server.py

# 2. Start Dashboard (in new terminal)
python run_dashboard.py

# 3. Test Pipeline
python pipeline.py --source files
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data models config .streamlit

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "api_server.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./config:/app/config
    environment:
      - DATA_DIR=/app/data
      - DB_PATH=/app/reconciliation.db
    command: python api_server.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./config:/app/config
    environment:
      - DATA_DIR=/app/data
    command: python run_dashboard.py
    depends_on:
      - api-server

  pipeline:
    build: .
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./config:/app/config
    environment:
      - DATA_DIR=/app/data
    command: python pipeline.py --source files
    depends_on:
      - api-server
```

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Setup

```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip nginx

# Clone repository
git clone https://github.com/your-repo/recon-ai.git
cd recon-ai

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/recon-ai
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Systemd Service

```ini
# /etc/systemd/system/recon-ai.service
[Unit]
Description=AI Reconciliation System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/recon-ai
Environment=PATH=/home/ubuntu/recon-ai/venv/bin
ExecStart=/home/ubuntu/recon-ai/venv/bin/python api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Azure Deployment

#### Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry your-registry --image recon-ai:latest .

# Deploy to Container Instances
az container create \
    --resource-group your-rg \
    --name recon-ai \
    --image your-registry.azurecr.io/recon-ai:latest \
    --ports 8000 8501 \
    --environment-variables DATA_DIR=/app/data
```

#### Azure App Service

```yaml
# .azure/config.yml
language: python
buildCommands:
  - pip install -r requirements.txt
startupCommand: python api_server.py
```

### Google Cloud Deployment

#### Cloud Run

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/your-project/recon-ai
gcloud run deploy recon-ai \
    --image gcr.io/your-project/recon-ai \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## 🔧 Environment Configuration

### Environment Variables

```bash
# .env file
DATA_DIR=/app/data
DB_PATH=/app/reconciliation.db
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_PORT=8501
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Configuration Files

```json
// api_config.json
{
  "base_url": "https://api.example.com",
  "api_key": "${API_KEY}",
  "timeout": 30,
  "retries": 3,
  "endpoints": {
    "old_pricing": "/api/v1/pricing/old",
    "new_pricing": "/api/v1/pricing/new",
    "trade_metadata": "/api/v1/trades/metadata",
    "funding_reference": "/api/v1/funding/reference"
  }
}
```

## 📊 Monitoring and Logging

### Logging Configuration

```python
# logging_config.py
import logging
import os

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('recon-ai.log'),
            logging.StreamHandler()
        ]
    )
```

### Health Checks

```python
# health_check.py
import requests
import time

def check_api_health():
    try:
        response = requests.get('http://localhost:8000/api/health')
        return response.status_code == 200
    except:
        return False

def check_dashboard_health():
    try:
        response = requests.get('http://localhost:8501')
        return response.status_code == 200
    except:
        return False
```

### Monitoring Script

```bash
#!/bin/bash
# monitor.sh

while true; do
    if ! curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "$(date): API server is down, restarting..."
        systemctl restart recon-ai
    fi
    
    if ! curl -f http://localhost:8501 > /dev/null 2>&1; then
        echo "$(date): Dashboard is down, restarting..."
        systemctl restart recon-dashboard
    fi
    
    sleep 60
done
```

## 🔐 Security Considerations

### SSL/TLS Configuration

```nginx
# SSL configuration for Nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        proxy_pass http://localhost:8501;
        # ... other proxy settings
    }
}
```

### Authentication

```python
# auth.py
from functools import wraps
from flask import request, jsonify
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing token'}), 401
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            request.user = payload
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated
```

## 🚀 Performance Optimization

### Production Settings

```python
# production_config.py
import os

# Performance settings
os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '200'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Memory optimization
import gc
gc.set_threshold(700, 10, 10)
```

### Caching

```python
# cache.py
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(key, data, expire=3600):
    redis_client.setex(key, expire, json.dumps(data))

def get_cached_result(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Dependencies updated
- [ ] Configuration files prepared
- [ ] Environment variables set
- [ ] Database migrations completed
- [ ] SSL certificates obtained
- [ ] Monitoring configured

### Deployment
- [ ] Backup existing data
- [ ] Deploy new version
- [ ] Run health checks
- [ ] Verify all services running
- [ ] Test API endpoints
- [ ] Test dashboard functionality
- [ ] Monitor error logs

### Post-Deployment
- [ ] Performance monitoring
- [ ] Error rate monitoring
- [ ] User feedback collection
- [ ] Documentation updates
- [ ] Team notification

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Your deployment commands
          echo "Deploying to production..."
```

## 📞 Support

### Troubleshooting Commands

```bash
# Check service status
systemctl status recon-ai

# View logs
journalctl -u recon-ai -f

# Restart services
systemctl restart recon-ai
systemctl restart nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check network connectivity
netstat -tulpn
```

### Emergency Procedures

1. **Service Down**: Restart services in order (API → Dashboard)
2. **Database Issues**: Restore from backup
3. **Performance Issues**: Scale up resources
4. **Security Breach**: Rotate credentials, review logs

---

**🚀 Happy Deploying!**

This deployment guide ensures your AI Reconciliation System runs smoothly in any environment. 