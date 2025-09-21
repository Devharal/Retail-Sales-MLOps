# Retail Sales MLOps Project
![Core Infrastructure](images/architech.png)
## About the Project

This is a production-grade MLOps project that builds an end-to-end machine learning pipeline for retail sales prediction. The project demonstrates real-world MLOps practices including:

- **Real-time Data Streaming**: Using Apache Kafka for streaming sales data
- **Data Storage**: PostgreSQL for structured data storage
- **Model Training & Tracking**: MLflow for experiment tracking and model versioning
- **Model Serving**: FastAPI for high-performance prediction API
- **Workflow Orchestration**: Apache Airflow for automated pipeline management
- **Monitoring & Observability**: Prometheus and Grafana for system and model monitoring
- **Web Interface**: React-based dashboard for business users

The pipeline ingests historical sales data, trains XGBoost models for sales forecasting, serves predictions via REST API, and provides comprehensive monitoring and alerting capabilities.

## Architecture Overview

The system consists of several microservices working together:
- **Data Producer**: Streams sales data to Kafka
- **Data Consumer**: Consumes Kafka messages and stores in PostgreSQL  
- **Training Service**: Handles model training with MLflow integration
- **Forecast Service**: Serves predictions via FastAPI
- **Airflow**: Orchestrates training and data pipeline workflows
- **Monitoring Stack**: Prometheus, Grafana, cAdvisor for observability
- **Web UI**: Dashboard for model insights and predictions

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available
- Python 3.9+ (for local development)
- Git

## Project Setup

### 1. Clone and Initialize Project

```bash
git clone <repository-url>
cd retail-sales-prediction
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Service Ports
NGINX_PORT=80
GRAFANA_PORT=3000
FORECAST_SERVICE_PORT=4242
TRAINING_SERVICE_PORT=4243
MLFLOW_PORT=5050
POSTGRES_PORT=5432
WEB_UI_PORT=8000
AIRFLOW_WEBSERVER_PORT=8080
KAFKA_UI_PORT=8800
CADVISOR_PORT=8089
PROMETHEUS_PORT=9090

# Data Configuration
KAFKA_TOPIC=sale_rossman_store
SALES_TABLE_NAME=rossman_sales
FORECAST_TABLE_NAME=forecast_results
MLFLOW_ARTIFACT_ROOT=/storage/mlruns/
MAIN_DB_PW=SuperSecurePwdHere

# Airflow Configuration
AIRFLOW_UID=501
AIRFLOW_PROJ_DIR=./services/airflow
```

### 3. Build All Services

Build all Docker images before starting services:

```bash
# Build all services
docker-compose build
```

## Service Startup Process

Follow this exact sequence to start all services properly:

### Step 1: Start Core Infrastructure
```bash
docker-compose up -d zookeeper kafka postgres

```

**Expected Result**: 
- Kafka available at `localhost:9092`
- PostgreSQL available at `localhost:5432`
- Wait 30-60 seconds for services to fully initialize



---

### Step 2: Start Data Pipeline
```bash
docker-compose up -d kafka-ui
docker-compose up -d data-producer
```

**Expected Result**:
- Data producer starts streaming sales data to Kafka
- Check logs: `docker-compose logs data-producer`


![Data Producer](images/kakfaui.png)
*Screenshot showing data producer logs streaming sales data*

---

### Step 3: Start Database Management
```bash
docker-compose up -d pgadmin
```

**Expected Result**:
- PgAdmin available at `localhost:5050`
- Login credentials: admin@admin.com / admin

**Setup Instructions:**
1. Navigate to `http://localhost:5050`
2. Login with admin@admin.com / admin
3. Add server connection:
   - Host: `postgres`
   - Port: `5432`
   - Database: `postgres`
   - Username: `postgres`
   - Password: `SuperSecurePwdHere`

![PgAdmin Setup](images/pgadmin_1.png)
![PgAdmin Setup](images/pgadmin_2.png)
*Screenshot showing PgAdmin login and server configuration*

---

### Step 4: Start Data Consumer
```bash
docker-compose up -d data-consumer
```

**Expected Result**:
- Consumer processes Kafka messages and stores in PostgreSQL
- Check data in PgAdmin: `SELECT * FROM rossman_sales LIMIT 10;`

---

### Step 5: Start MLflow
```bash
docker-compose up -d mlflow
```

**Expected Result**:
- MLflow UI available at `localhost:5050`
- Experiment tracking ready

**Verification:**
1. Navigate to `http://localhost:5050`
2. You should see MLflow tracking UI
3. Initially no experiments will be visible



---

### Step 6: Start Training Service
```bash
docker-compose up -d training-service
```

**Expected Result**:
- Training API available at `localhost:4243`
- Swagger docs at `localhost:4243/docs`

**Verification:**
1. Navigate to `http://localhost:4243/docs`
2. You should see FastAPI Swagger documentation
3. Test the `/health` endpoint

![MLflow UI](images/mlflow1.png)
*Screenshot showing MLflow UI interface*

---

### Step 7: Start Airflow
```bash
docker-compose up -d airflow-webserver airflow-scheduler airflow-init
```

**Expected Result**:
- Airflow UI available at `localhost:8080`
- Login: airflow/airflow
- DAGs should be visible in the UI

**Setup Instructions:**
1. Navigate to `http://localhost:8080`
2. Login with airflow/airflow
3. You should see the DAGs listed
4. Enable the DAGs by toggling them on

![Airflow UI](images/airflow1.png)
*Screenshot showing Airflow web interface with DAGs*

---

### Step 8: Start Forecast Service  
```bash
docker-compose up -d forecast-service
```

**Expected Result**:
- Forecast API available at `localhost:4242`
- Swagger docs at `localhost:4242/docs`

**Verification:**
1. Navigate to `http://localhost:4242/docs`
2. Test the `/health` endpoint
3. Try the `/model/info` endpoint

---

### Step 9: Start Monitoring Stack
```bash
docker-compose up -d prometheus grafana cadvisor node-exporter
```

**Expected Result**:
- Prometheus UI at `localhost:9090`
- Grafana at `localhost:3000` (admin/admin)
- cAdvisor at `localhost:8089`

**Setup Instructions:**

**Grafana (`http://localhost:3000`):**
1. Login with admin/admin
2. Import dashboards from Configuration > Dashboards
3. Configure data sources (Prometheus should be auto-configured)

![Grafana Dashboard](images/grafan1.png)
![Grafana Dashboard](images/grafan2.png)
*Screenshot showing Grafana monitoring dashboards*

**cAdvisor (`http://localhost:8089`):**
1. Navigate to view container metrics
2. Check resource utilization


---

### Step 10: Start Web Interface
```bash
docker-compose up -d --build nginx web-ui
```

**Expected Result**:
- Web UI available at `localhost:80`
- Business dashboard with prediction interface

**Alternative command if above fails:**
```bash
docker-compose up -d nginx web-ui
```

**Verification:**
1. Navigate to `http://localhost:80`
2. You should see the business dashboard
3. Try making a prediction through the UI

![Web UI Dashboard](images/webui1.png)
*Screenshot showing the main web dashboard*


## Service Access URLs

Once all services are running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| Web UI | http://localhost:80 | - |
| Forecast API | http://localhost:4242/docs | - |
| Training API | http://localhost:4243/docs | - |
| MLflow | http://localhost:5050 | - |
| Airflow | http://localhost:8080 | airflow/airflow |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| PgAdmin | http://localhost:5050 | admin@admin.com/admin |
| cAdvisor | http://localhost:8089 | - |

## Testing the Pipeline

### 1. Verify Data Flow
```bash
# Check if data is flowing to database
docker-compose exec postgres psql -U postgres -c "SELECT COUNT(*) FROM rossman_sales;"
```


### 2. Train a Model
```bash
curl -X POST "http://localhost:4243/train" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "start_date": "2023-01-01",
    "end_date": "2023-06-30"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "run_id": "a1b2c3d4e5f6789012345678",
  "metrics": {
    "r2": 0.85,
    "mse": 125000.5,
    "rmse": 353.55,
    "mae": 285.42
  }
}
```

**Verify in MLflow UI:**
Navigate to `http://localhost:5050` to see the experiment results

![MLflow Experiment](images/test2-mlflow-experiment.png)
*Screenshot showing MLflow experiment with metrics*

---

### 3. Make a Prediction
```bash
curl -X POST "http://localhost:4242/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "date": "2024-01-01",
    "promo": 1,
    "stateholiday": "0",
    "schoolholiday": 0
  }'
```

**Expected Response:**
```json
{
  "store_id": 1,
  "date": "2024-01-01",
  "predicted_sales": 5847.32,
  "model_version": "a1b2c3d4e5f6789012345678"
}
```

**Verify Prediction Storage:**
Check in PgAdmin: `SELECT * FROM forecast_results ORDER BY prediction_timestamp DESC LIMIT 5;`

![Prediction Results](images/test3-prediction-results.png)
*Screenshot showing prediction results in database*

---

### 4. Test via Swagger UI
Navigate to `http://localhost:4242/docs` and test the prediction endpoint interactively:

![Swagger Testing](images/test4-swagger-testing.png)
*Screenshot showing Swagger UI prediction test*

---

### 5. Check Monitoring
Visit Grafana at `localhost:3000` to view:
- System metrics
- API response times  
- Model performance metrics
- Data pipeline health

**Setup Grafana Dashboard:**
1. Login with admin/admin
2. Import dashboard JSON files from the project
3. Configure Prometheus datasource if not auto-configured

![Grafana Metrics](images/test5-grafana-metrics.png)
*Screenshot showing Grafana dashboard with system metrics*

---

### 6. Test Airflow Workflows
1. Navigate to `http://localhost:8080`
2. Enable the `train_predict_to_db` DAG
3. Trigger a manual run
4. Monitor the execution

---

### 7. End-to-End Pipeline Test
Run the complete pipeline test to verify all components work together:

```bash
# Trigger training via Airflow
curl -X POST "http://localhost:8080/api/v1/dags/train_predict_to_db/dagRuns" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'airflow:airflow' | base64)" \
  -d '{"conf": {"store_id": 1}}'
```

**Monitor the complete flow:**
1. Check Airflow for DAG execution status
2. Verify new model in MLflow
3. Test prediction with the new model
4. Check monitoring dashboards for metrics updates



### Stopping Services

To stop all services and clean up:
```bash
docker-compose down -v
```

**Warning**: This will remove all data including trained models and database content.

To stop without removing volumes:
```bash
docker-compose down
```


## Next Steps

- Explore Kubernetes deployment (Week 7 of the learning guide)
- Set up CI/CD pipelines  
- Configure production monitoring and alerting
- Scale services based on load requirements
