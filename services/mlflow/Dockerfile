FROM python:3.9-slim

# Set working directory
WORKDIR /mlflow

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the MLflow server command
# CMD mlflow server \
#     --host 0.0.0.0 \
#     --port $MLFLOW_PORT \
#     --backend-store-uri postgresql://${POSTGRES_USER}:${MAIN_DB_PW}@postgres:${POSTGRES_PORT}/postgres \
#     --default-artifact-root /storage/mlruns/

CMD mlflow server \
    --host 0.0.0.0 \
    --port ${MLFLOW_PORT:-5050} \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root /storage/mlruns/
