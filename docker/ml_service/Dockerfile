FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libpq-dev curl libcairo2 libpango-1.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ml_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ml_service/ .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
