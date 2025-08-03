# FROM python:3.9-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY scripts/ ./scripts/
# COPY datasets/ ./datasets/

# CMD ["python", "scripts/kafka_producer.py"]
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY datasets/ ./datasets/

# CMD ["sh", "-c", "python scripts/put_data_in_postgres.py && python scripts/kafka_producer.py"]
CMD ["bash", "-c", "python scripts/put_data_in_postgres.py && python scripts/kafka_producer.py"]
