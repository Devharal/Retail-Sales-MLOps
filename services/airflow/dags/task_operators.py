
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import requests
import logging
import mlflow

logger = logging.getLogger(__name__)

class ModelTrainingOperator(BaseOperator):
    @apply_defaults
    def __init__(self, endpoint_url, training_params, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint_url = endpoint_url
        self.training_params = training_params

    def execute(self, context):
        try:
            response = requests.post(self.endpoint_url, json=self.training_params)
            response.raise_for_status()
            logger.info(f"Training completed: {response.json()}")
            return response.json()['run_id']
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise

class ModelValidationOperator(BaseOperator):
    @apply_defaults
    def __init__(self, mlflow_tracking_uri, experiment_name, rmse_threshold=1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.experiment_name = experiment_name
        self.rmse_threshold = rmse_threshold

    def execute(self, context):
        try:
            client = mlflow.tracking.MlflowClient(tracking_uri=self.mlflow_tracking_uri)
            experiment = client.get_experiment_by_name(self.experiment_name)
            runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["metrics.rmse ASC"], max_results=1)
            if not runs:
                raise ValueError("No runs found in MLflow")
            latest_run = runs[0]
            rmse = latest_run.data.metrics.get("rmse", float("inf"))
            if rmse > self.rmse_threshold:
                raise ValueError(f"Model RMSE {rmse} exceeds threshold {self.rmse_threshold}")
            logger.info(f"Model validation successful: RMSE={rmse}")
            return latest_run.info.run_id
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise