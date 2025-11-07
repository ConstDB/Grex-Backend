FROM python:3.13-slim

# Install dependencies needed for psycopg2, numpy, scipy, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /

# Install Torch separately with CPU wheel
RUN pip install --no-cache-dir torch==2.8.0+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Install other requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

# Expose port
EXPOSE 8000

# # Use uvicorn to serve FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
