FROM python:3.11-slim

WORKDIR /app

# Install system deps for ChromaDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create workspace and chromadb directories
RUN mkdir -p /app/workspace /app/chromadb

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
