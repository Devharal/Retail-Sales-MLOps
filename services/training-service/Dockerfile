FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/

# Start the FastAPI training service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4243", "--reload"]
