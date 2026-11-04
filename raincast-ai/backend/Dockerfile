FROM python:3.11-slim

# Install ecCodes (required for cfgrib/GRIB2 processing)
RUN apt-get update && apt-get install -y \
    libeccodes-dev \
    libeccodes-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create cache directory
RUN mkdir -p /app/cache

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
