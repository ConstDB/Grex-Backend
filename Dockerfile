FROM python:3.13-slim

# Install dependencies needed for psycopg2, numpy, scipy, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Torch separately with CPU wheel
RUN pip install --no-cache-dir torch==2.8.0+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Copy requirement file first (better for caching)
COPY requirements.txt /app/requirements.txt

# Set working directory early
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
