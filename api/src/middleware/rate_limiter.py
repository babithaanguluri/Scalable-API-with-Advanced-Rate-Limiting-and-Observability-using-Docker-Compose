import time
import os
from fastapi import Request, HTTPException
from redis import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# Bucket Capacity
MAX_TOKENS = int(os.getenv("RATE_LIMIT", 5))  
# Tokens added per second
REFILL_RATE = float(os.getenv("REFILL_RATE", 0.1)) 

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class TokenBucketMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We only apply rate limiting to /api/protected-action as per requirements
        if request.url.path != "/api/protected-action":
            return await call_next(request)

        client_ip = request.client.host
        key = f"token_bucket:{client_ip}"
        now = time.time()

        # Get current bucket state
        # State stored as a hash: "tokens", "last_refill"
        state = redis_client.hgetall(key)
        
        if not state:
            tokens = MAX_TOKENS
            last_refill = now
        else:
            last_tokens = float(state["tokens"])
            last_refill = float(state["last_refill"])
            
            # Refill tokens
            elapsed = now - last_refill
            refilled = elapsed * REFILL_RATE
            tokens = min(MAX_TOKENS, last_tokens + refilled)

        # Decide if request is allowed
        if tokens >= 1:
            tokens -= 1
            redis_client.hset(key, mapping={
                "tokens": tokens,
                "last_refill": now
            })
            redis_client.expire(key, 3600)  # TTL of 1 hour for inactive buckets
            
            response = await call_next(request)
            
            # Add headers
            response.headers["X-RateLimit-Limit"] = str(MAX_TOKENS)
            response.headers["X-RateLimit-Remaining"] = str(int(tokens))
            response.headers["X-RateLimit-Reset"] = str(int(now + (MAX_TOKENS - tokens) / REFILL_RATE))
            
            return response
        else:
            # 429 Too Many Requests
            reset_time = int(now + (1 - tokens) / REFILL_RATE)
            return Response(
                content="Too Many Requests",
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(MAX_TOKENS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time)
                }
            )
