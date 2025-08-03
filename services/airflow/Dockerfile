# FROM apache/airflow:2.5.0-python3.9
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY dags/ /opt/airflow/dags/
# COPY plugins/ /opt/airflow/plugins/
FROM apache/airflow:2.7.2-python3.9

USER root

# Install required system packages
RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Set environment variable (optional if already set by base image)
ENV AIRFLOW_HOME=/opt/airflow

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
