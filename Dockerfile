# Stage 1: Build environment
FROM python:3.9-slim AS builder
WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-slim
WORKDIR /app
ENV PYTHONPATH=/app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8080
CMD ["python", "./api/src/main.py"]
