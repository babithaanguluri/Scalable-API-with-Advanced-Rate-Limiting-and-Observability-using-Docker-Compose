import time
from typing import List, Any
from fastapi import FastAPI, Request, status, Body
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from api.src.middleware.rate_limiter import TokenBucketMiddleware
from api.src.models.product import Product, ProductCreate

app = FastAPI(title="Scalable API with Token Bucket Rate Limiting")
app.add_middleware(TokenBucketMiddleware)

# In-memory storage for products (for demonstration purposes)
products_db: List[Product] = []

# Prometheus Metrics
REQUEST_COUNT = Counter("api_requests_total", "Total count of requests", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "Latency of requests in seconds", ["method", "endpoint"])

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(latency)
    
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join([str(loc) for loc in error["loc"]])
        msg = error["msg"]
        input_val = error.get("input", "N/A")
        errors.append({
            "field": field,
            "message": f"{msg}. Received: '{input_val}'",
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation failed for the request body.",
            "errors": errors
        }
    )

@app.get("/api/status")
async def get_status():
    return {"status": "healthy"}

@app.post("/api/products", status_code=status.HTTP_201_CREATED, response_model=Product)
async def create_product(product_in: ProductCreate):
    new_product = Product(**product_in.dict())
    products_db.append(new_product)
    return new_product

@app.get("/api/products", response_model=List[Product])
async def get_products():
    return products_db

@app.post("/api/protected-action")
async def protected_action(payload: Any = Body(...)):
    return {"message": "Action performed successfully", "data": payload}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
