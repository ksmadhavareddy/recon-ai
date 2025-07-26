# Reconciliation Data REST API Documentation

## Overview

The Reconciliation Data REST API provides programmatic access to reconciliation data from Excel files and databases. The API is built with FastAPI and offers comprehensive endpoints for data retrieval, searching, and analysis.

## Features

- **Excel File Access**: Read data from Excel files in the data directory
- **Database Integration**: Access SQLite database with merged reconciliation data
- **Search Capabilities**: Search across tables and columns
- **Pagination**: Support for large datasets with limit/offset pagination
- **Health Monitoring**: Built-in health check endpoint
- **CORS Support**: Cross-origin resource sharing enabled
- **Auto-generated Documentation**: Interactive API docs at `/docs`

## Quick Start

### 1. Start the API Server

```bash
python api_server.py
```

The server will start on `http://localhost:8000`

### 2. Access API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

### 3. Test the API

```bash
python api_client.py
```

## API Endpoints

### Root Endpoint

**GET /** - API Information
```json
{
  "message": "Reconciliation Data API",
  "version": "1.0.0",
  "endpoints": {
    "excel": "/api/excel",
    "database": "/api/database",
    "merged": "/api/merged",
    "search": "/api/search"
  }
}
```

### Excel Data Endpoints

#### GET /api/excel
Get list of available Excel files

**Response:**
```json
{
  "files": [
    {
      "filename": "old_pricing.xlsx",
      "size_bytes": 8192,
      "modified": "2024-01-15T10:30:00",
      "path": "data/old_pricing.xlsx"
    }
  ],
  "total_files": 4
}
```

#### GET /api/excel/{filename}
Get data from specific Excel file

**Parameters:**
- `filename` (path): Name of the Excel file

**Response:**
```json
{
  "filename": "old_pricing.xlsx",
  "rows": 21,
  "columns": ["TradeID", "PV_old", "Delta_old"],
  "data": [
    {
      "TradeID": "TRADE001",
      "PV_old": 1000000.0,
      "Delta_old": 0.5
    }
  ],
  "summary": {
    "total_rows": 21,
    "total_columns": 3,
    "column_types": {
      "TradeID": "object",
      "PV_old": "float64",
      "Delta_old": "float64"
    }
  }
}
```

### Database Endpoints

#### GET /api/database
Get database information and available tables

**Response:**
```json
{
  "database_path": "reconciliation.db",
  "tables": ["old_pricing", "new_pricing", "trade_metadata", "funding_model_reference"],
  "total_tables": 4
}
```

#### GET /api/database/{table}
Get data from specific database table

**Parameters:**
- `table` (path): Name of the database table
- `limit` (query, optional): Number of records to return (default: 100, max: 1000)
- `offset` (query, optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "table": "old_pricing",
  "total_rows": 21,
  "returned_rows": 10,
  "columns": ["TradeID", "PV_old", "Delta_old"],
  "data": [
    {
      "TradeID": "TRADE001",
      "PV_old": 1000000.0,
      "Delta_old": 0.5
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

#### GET /api/merged
Get merged reconciliation data

**Parameters:**
- `limit` (query, optional): Number of records to return (default: 100, max: 1000)
- `offset` (query, optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "data_type": "merged_reconciliation_data",
  "total_rows": 21,
  "returned_rows": 10,
  "columns": ["TradeID", "PV_old", "PV_new", "Delta_old", "Delta_new", "TradeType", "Counterparty"],
  "data": [
    {
      "TradeID": "TRADE001",
      "PV_old": 1000000.0,
      "PV_new": 1000500.0,
      "Delta_old": 0.5,
      "Delta_new": 0.52,
      "TradeType": "IRS",
      "Counterparty": "Bank A"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

### Search Endpoints

#### GET /api/search
Search data in specified table

**Parameters:**
- `table` (query): Name of the database table to search
- `search_term` (query): Search term to look for
- `column` (query, optional): Specific column to search in

**Response:**
```json
{
  "table": "trade_metadata",
  "search_term": "IRS",
  "searched_column": null,
  "results_count": 5,
  "data": [
    {
      "TradeID": "TRADE001",
      "TradeType": "IRS",
      "Counterparty": "Bank A",
      "Notional": 10000000.0
    }
  ]
}
```

### Health Check

#### GET /api/health
Check API health status

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "data_dir": "data/",
  "database_exists": true
}
```

## Usage Examples

### Python Client

```python
from api_client import ReconciliationAPIClient

# Initialize client
client = ReconciliationAPIClient("http://localhost:8000")

# Health check
health = client.health_check()
print(health)

# Get Excel files
files = client.get_excel_files()
print(f"Available files: {files['total_files']}")

# Get Excel data
data = client.get_excel_data("old_pricing.xlsx")
print(f"Rows: {data['rows']}")

# Get database info
db_info = client.get_database_info()
print(f"Tables: {db_info['tables']}")

# Get table data
table_data = client.get_table_data("old_pricing", limit=10)
print(f"Total rows: {table_data['total_rows']}")

# Get merged data
merged = client.get_merged_data(limit=20)
print(f"Columns: {merged['columns']}")

# Search data
search_results = client.search_data("trade_metadata", "IRS")
print(f"Found {search_results['results_count']} results")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/api/health

# Get Excel files
curl http://localhost:8000/api/excel

# Get Excel data
curl http://localhost:8000/api/excel/old_pricing.xlsx

# Get database info
curl http://localhost:8000/api/database

# Get table data
curl "http://localhost:8000/api/database/old_pricing?limit=10&offset=0"

# Get merged data
curl "http://localhost:8000/api/merged?limit=20"

# Search data
curl "http://localhost:8000/api/search?table=trade_metadata&search_term=IRS"
```

### JavaScript/Fetch Examples

```javascript
// Health check
fetch('http://localhost:8000/api/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Get Excel files
fetch('http://localhost:8000/api/excel')
  .then(response => response.json())
  .then(data => console.log(data.files));

// Get merged data with pagination
fetch('http://localhost:8000/api/merged?limit=50&offset=0')
  .then(response => response.json())
  .then(data => {
    console.log(`Total rows: ${data.total_rows}`);
    console.log(`Data: ${data.data}`);
  });

// Search data
fetch('http://localhost:8000/api/search?table=trade_metadata&search_term=IRS')
  .then(response => response.json())
  .then(data => console.log(data.results_count));
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (file/table doesn't exist)
- **500**: Internal Server Error

Error responses include details:

```json
{
  "detail": "File old_pricing.xlsx not found"
}
```

## Database Schema

The API automatically creates a SQLite database with the following structure:

### Tables
- `old_pricing`: Old pricing data
- `new_pricing`: New pricing data  
- `trade_metadata`: Trade metadata
- `funding_model_reference`: Funding model data

### Views
- `merged_data`: Combined view of all tables joined on TradeID

## Configuration

### Environment Variables
- `DATA_DIR`: Directory containing Excel files (default: "data/")
- `DB_PATH`: SQLite database path (default: "reconciliation.db")
- `API_HOST`: API server host (default: "0.0.0.0")
- `API_PORT`: API server port (default: 8000)

### Customization
Modify `api_server.py` to:
- Add new endpoints
- Change database type (PostgreSQL, MySQL, etc.)
- Add authentication
- Implement caching
- Add rate limiting

## Integration with Existing System

The API integrates seamlessly with the existing reconciliation system:

1. **Data Loading**: API provides data to existing agents
2. **Dashboard Integration**: Streamlit dashboard can use API data
3. **Pipeline Integration**: Pipeline can fetch data via API
4. **External Systems**: Other systems can consume reconciliation data

## Performance Considerations

- **Pagination**: Use limit/offset for large datasets
- **Caching**: Consider implementing Redis for frequently accessed data
- **Database Indexing**: SQLite automatically indexes primary keys
- **Connection Pooling**: FastAPI handles connection pooling automatically

## Security

- **CORS**: Configured for development (allow all origins)
- **Input Validation**: FastAPI validates all inputs
- **SQL Injection**: Protected by parameterized queries
- **File Access**: Restricted to data directory

## Monitoring

- **Health Check**: `/api/health` endpoint
- **Logging**: Structured logging with Python logging
- **Metrics**: Consider adding Prometheus metrics
- **Error Tracking**: Log all errors with context

## Troubleshooting

### Common Issues

1. **API not accessible**
   - Check if server is running: `python api_server.py`
   - Verify port 8000 is available
   - Check firewall settings

2. **Database not found**
   - API automatically creates database on first run
   - Check file permissions for data directory
   - Verify Excel files exist in data directory

3. **Large response times**
   - Use pagination (limit parameter)
   - Consider implementing caching
   - Check database performance

4. **CORS errors**
   - Configure CORS middleware for your domain
   - Check browser console for specific errors

### Debug Mode

Run with debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Authentication**: JWT token-based authentication
- **Rate Limiting**: API rate limiting
- **Caching**: Redis-based caching
- **Webhooks**: Real-time data updates
- **GraphQL**: Alternative to REST API
- **Real-time**: WebSocket support
- **Analytics**: Usage analytics and metrics 

# Model Selection Rationale: Why LightGBM?

For the MLDiagnoserAgent, we chose **LightGBM** as the primary model for the following reasons:

- **Scalability:** LightGBM is specifically designed for large-scale datasets and can efficiently handle 100+ million records.
- **Speed:** It is faster than most other gradient boosting frameworks (including CatBoost and XGBoost) for both training and prediction, especially on large tabular data.
- **Memory Efficiency:** LightGBM uses a histogram-based algorithm that is highly memory efficient, making it suitable for big data scenarios.
- **Native Categorical Support:** LightGBM can natively handle categorical features, reducing the need for extensive preprocessing and improving model performance.
- **Distributed and GPU Training:** LightGBM supports distributed training across multiple machines and GPU acceleration, which is essential for scaling up in production environments.

**Comparison with Other Models:**
- **CatBoost:** While CatBoost also handles categorical features natively and is robust, it is generally slower than LightGBM for extremely large datasets.
- **XGBoost:** XGBoost is highly tunable and scalable, but LightGBM is typically faster and more memory efficient for very large tabular datasets.
- **RandomForest/LogisticRegression:** These models are not suitable for 100M+ records due to speed and memory limitations.

**Conclusion:**
LightGBM offers the best trade-off between speed, scalability, and ease of use for large tabular datasets with categorical features, making it the optimal choice for our production-scale MLDiagnoserAgent. 