# Scalable API with Token Bucket Rate Limiting and Observability

This project demonstrates a production-ready API setup with:
- **FastAPI**: Modern web framework for the API.
- **Redis (Token Bucket)**: Advanced rate limiting using the Token Bucket algorithm.
- **Prometheus**: Monitoring and metrics collection.
- **Grafana**: Real-time metrics visualization.
- **Docker Compose**: Seamless orchestration of all services.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Returns API health status. |
| `POST` | `/api/products` | Create a new product. Example body: `{"name": "Laptop", "description": "High-end PC", "price": 999.99}` |
| `GET` | `/api/products` | Retrieve all products. |
| `POST` | `/api/protected-action` | **Rate-limited** endpoint with Token Bucket. |
| `GET` | `/metrics` | Prometheus metrics. |

## Rate Limiting (Token Bucket)

The API implements a Token Bucket algorithm via Redis. 
- **Capacity**: `RATE_LIMIT` (default: 5 tokens).
- **Refill Rate**: `REFILL_RATE` (default: 0.1 tokens per second).
- **Headers**:
  - `X-RateLimit-Limit`: Maximum tokens.
  - `X-RateLimit-Remaining`: Remaining tokens in the bucket.
  - `X-RateLimit-Reset`: Estimated time when the bucket will be full.

## Getting Started

1.  **Initialize the Environment**:
    ```bash
    cp .env.example .env
    ```

2.  **Start the Stack**:
    ```bash
    docker-compose up -d --build
    ```

3.  **Usage**:
    - **FastAPI Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
    - **Grafana**: [http://localhost:3000](http://localhost:3000) (`admin`/`admin`)

## Running Tests

The project includes a comprehensive test suite with unit and integration tests.

### Local Tests (Docker)
To run the tests inside the containerized environment:
```bash
docker-compose exec api_service pytest ./api/src/tests/test_unit.py ./api/src/tests/test_integration.py
```

### Test Coverage
- **Unit Tests**: Validates product model constraints and ID generation.
- **Integration Tests**: Verifies API endpoints, including health checks, product creation, and rate-limited actions.
