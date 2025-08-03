import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd
from db_utils import DatabaseConnection
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def fetch_training_data():
    db = DatabaseConnection()
    db.connect()
    
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    df = db.get_sales_data(start_date=start_date, end_date=end_date)
    
    if df.empty:
        raise ValueError("No training data available")
    logger.info("Fetched training data tail:\n%s", df.tail())
    # Assume one store for simplicity
    store = int(df["store"].iloc[0])
    
    return {
        "store": store,
        "start_date": start_date,
        "end_date": end_date
    }


def trigger_model_training(**context):
    data = context['ti'].xcom_pull(task_ids='fetch_training_data')
    response = requests.post(
        "http://training-service:4243/train",
        json={
            **data,
            "params": {
                "max_depth": 6,
                "learning_rate": 0.1,
                "n_estimators": 100
            }
        }
    )
    return response.json()['run_id']

def validate_model_performance(**context):
    run_id = context['ti'].xcom_pull(task_ids='trigger_model_training')
    response = requests.get(f"http://training-service:4243/models/{run_id}")
    metrics = response.json()['metrics']
    if metrics['r2'] < 0.7:
        raise Exception(f"Model R2 too low: {metrics['r2']}")
    return metrics

with DAG(
    'train_predict_to_db',
    default_args=default_args,
    schedule_interval='* * * * *',  # Every minute
    start_date=datetime(2023, 1, 1),
    catchup=False
) as dag:

    fetch_data = PythonOperator(task_id='fetch_training_data', python_callable=fetch_training_data)
    train_model = PythonOperator(task_id='trigger_model_training', python_callable=trigger_model_training)
    validate_model = PythonOperator(task_id='validate_model_performance', python_callable=validate_model_performance)

    fetch_data >> train_model >> validate_model