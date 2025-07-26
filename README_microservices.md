# 🤖 AI Reconciliation System - Microservices Architecture

This document describes the microservices-based architecture for the AI-powered reconciliation system.

## 🏗️ Architecture Overview

The system has been refactored from a monolithic application to a **microservices architecture** with the following services:

### 📊 Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   Orchestrator   │    │   Data Service  │
│   (Streamlit)   │◄──►│   Service        │◄──►│   (Port 8001)   │
└─────────────────┘    │   (Port 8005)    │    └─────────────────┘
                       └──────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  ML Service     │    │ Reconciliation    │    │ Report Service  │
│  (Port 8003)    │    │ Service          │    │ (Port 8004)     │
└─────────────────┘    │ (Port 8002)      │    └─────────────────┘
                       └──────────────────┘
```

## 🚀 Services

### 1. **Data Service** (Port 8001)
- **Purpose**: Handles data loading, merging, and validation
- **Endpoints**:
  - `POST /load/files` - Load data from Excel files
  - `POST /load/api` - Load data from API
  - `POST /load/hybrid` - Load data using hybrid approach
  - `POST /validate` - Validate data quality
  - `GET /sources/available` - Get available data sources

### 2. **Reconciliation Service** (Port 8002)
- **Purpose**: Handles mismatch detection and rule-based analysis
- **Endpoints**:
  - `POST /detect-mismatches` - Detect PV/Delta mismatches
  - `POST /apply-diagnosis` - Apply rule-based diagnosis
  - `POST /full-reconciliation` - Complete reconciliation workflow
  - `GET /trade/{trade_id}` - Get trade details
  - `GET /summary` - Get reconciliation summary
  - `GET /config/tolerances` - Get/update tolerance settings

### 3. **ML Service** (Port 8003)
- **Purpose**: Handles machine learning model training and predictions
- **Endpoints**:
  - `POST /train` - Train ML model
  - `POST /predict` - Generate ML predictions
  - `POST /compare` - Compare ML vs rule-based predictions
  - `GET /model/info` - Get model information
  - `POST /validate-training-data` - Validate training data
  - `POST /model/reset` - Reset model

### 4. **Report Service** (Port 8004)
- **Purpose**: Handles report generation and export functionality
- **Endpoints**:
  - `POST /summary` - Generate summary report
  - `POST /detailed` - Generate detailed report (Excel/CSV)
  - `POST /narrative` - Generate narrative report
  - `GET /list` - List available reports
  - `GET /download/{filename}` - Download report
  - `DELETE /delete/{filename}` - Delete report
  - `GET /formats/available` - Get available formats

### 5. **Orchestrator Service** (Port 8005)
- **Purpose**: Coordinates between all other services
- **Endpoints**:
  - `GET /services/health` - Check health of all services
  - `GET /services/status` - Get comprehensive service status
  - `POST /workflow/run` - Run complete reconciliation workflow
  - `POST /workflow/cleanup/{workflow_id}` - Cleanup workflow resources
  - `GET /workflow/config` - Get workflow configuration

## 🛠️ Getting Started

### Prerequisites
```bash
pip install fastapi uvicorn httpx streamlit plotly
```

### 1. Start All Services
```bash
python service_manager.py start
```

### 2. Check Service Status
```bash
python service_manager.py status
```

### 3. Run Dashboard
```bash
streamlit run microservices_dashboard.py
```

### 4. Test Orchestrator
```bash
python service_manager.py test
```

## 📋 Service Management Commands

### Start Services
```bash
# Start all services
python service_manager.py start

# Start specific service
python service_manager.py start data_service
```

### Stop Services
```bash
# Stop all services
python service_manager.py stop

# Stop specific service
python service_manager.py stop ml_service
```

### Restart Services
```bash
# Restart all services
python service_manager.py restart

# Restart specific service
python service_manager.py restart report_service
```

### Check Status
```bash
# Show all service status
python service_manager.py status
```

## 🔄 Workflow Execution

### Via Orchestrator Service
```python
import requests

# Run complete workflow
response = requests.post("http://localhost:8005/workflow/run", json={
    "data_source": "files",
    "data_dir": "data",
    "pv_tolerance": 1000,
    "delta_tolerance": 0.05,
    "train_ml": True,
    "generate_reports": True
})

workflow_result = response.json()
```

### Via Individual Services
```python
# 1. Load data
response = requests.post("http://localhost:8001/load/files", 
                       params={"data_dir": "data"})

# 2. Run reconciliation
response = requests.post("http://localhost:8002/full-reconciliation",
                       json={"data": data_result["data"]})

# 3. Train ML model
response = requests.post("http://localhost:8003/train",
                       json={"data": recon_result["data"]})

# 4. Generate reports
response = requests.post("http://localhost:8004/detailed",
                       json={"data": recon_result["data"]})
```

## 🏗️ Architecture Benefits

### 1. **Scalability**
- Each service can scale independently
- ML service can use GPU resources
- Report service can handle heavy I/O operations

### 2. **Maintainability**
- Services can be developed and deployed independently
- Clear separation of concerns
- Easier to test individual components

### 3. **Resilience**
- Failure in one service doesn't bring down the entire system
- Services can be restarted independently
- Health checks for each service

### 4. **Technology Flexibility**
- Each service can use the best technology for its purpose
- Easy to replace or upgrade individual services
- Language-agnostic (can mix Python, Java, Go, etc.)

### 5. **Deployment Flexibility**
- Services can be deployed on different servers
- Container-friendly (Docker, Kubernetes)
- Cloud-native architecture

## 🔧 Configuration

### Service URLs
All services run on localhost with different ports:
- Data Service: `http://localhost:8001`
- Reconciliation Service: `http://localhost:8002`
- ML Service: `http://localhost:8003`
- Report Service: `http://localhost:8004`
- Orchestrator Service: `http://localhost:8005`

### Environment Variables
```bash
# Service ports (optional, defaults shown)
DATA_SERVICE_PORT=8001
RECONCILIATION_SERVICE_PORT=8002
ML_SERVICE_PORT=8003
REPORT_SERVICE_PORT=8004
ORCHESTRATOR_SERVICE_PORT=8005
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
Each service provides a health check endpoint:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

### Service Status Dashboard
The orchestrator service provides comprehensive status:
```bash
curl http://localhost:8005/services/status
```

## 🚀 Deployment Options

### 1. **Local Development**
```bash
python service_manager.py start
streamlit run microservices_dashboard.py
```

### 2. **Docker Deployment**
```dockerfile
# Example Dockerfile for each service
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY services/ ./services/
CMD ["python", "services/data_service.py"]
```

### 3. **Kubernetes Deployment**
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: data-service
  template:
    metadata:
      labels:
        app: data-service
    spec:
      containers:
      - name: data-service
        image: reconciliation/data-service:latest
        ports:
        - containerPort: 8001
```

## 🔍 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check if port is in use
   netstat -an | grep 8001
   
   # Kill process using port
   lsof -ti:8001 | xargs kill -9
   ```

2. **Service Health Check Fails**
   ```bash
   # Check service logs
   python service_manager.py status
   
   # Restart specific service
   python service_manager.py restart data_service
   ```

3. **Workflow Fails**
   ```bash
   # Check all service health
   curl http://localhost:8005/services/health
   
   # Test orchestrator
   python service_manager.py test
   ```

## 📈 Performance Considerations

### 1. **Service Communication**
- Use async/await for better performance
- Implement connection pooling
- Consider message queues for heavy workloads

### 2. **Data Transfer**
- Compress large datasets
- Use efficient serialization (Protocol Buffers, MessagePack)
- Implement pagination for large results

### 3. **Caching**
- Cache frequently accessed data
- Use Redis for shared caching
- Implement service-level caching

## 🔐 Security Considerations

### 1. **Authentication**
- Implement API key authentication
- Use JWT tokens for service-to-service communication
- Implement role-based access control

### 2. **Network Security**
- Use HTTPS for all communications
- Implement rate limiting
- Use firewalls to restrict service access

### 3. **Data Security**
- Encrypt sensitive data in transit and at rest
- Implement data validation at service boundaries
- Use secure configuration management

## 🚀 Future Enhancements

### 1. **Service Discovery**
- Implement service registry (Consul, etcd)
- Dynamic service discovery
- Load balancing

### 2. **Message Queues**
- Implement RabbitMQ or Apache Kafka
- Asynchronous processing
- Event-driven architecture

### 3. **Monitoring & Observability**
- Implement distributed tracing (Jaeger)
- Centralized logging (ELK stack)
- Metrics collection (Prometheus)

### 4. **API Gateway**
- Implement Kong or similar
- Rate limiting and throttling
- API versioning

---

## 📞 Support

For issues and questions:
1. Check service logs: `python service_manager.py status`
2. Test individual services: `python service_manager.py test`
3. Review this documentation
4. Check the original monolithic code for reference

The microservices architecture provides a solid foundation for scaling and maintaining the AI reconciliation system while preserving all the original functionality. 