import os
import mlflow
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.mlflow_tracking_uri = f"http://mlflow:{os.getenv('MLFLOW_PORT')}"
        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        self.experiment_name = "retail_sales_prediction"

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        df['stateholiday'] = df['stateholiday'].map({'0': 0, 'a': 1, 'b': 2, 'c': 3})

        feature_columns = [
            'store', 'year', 'month', 'day', 'day_of_week',
            'promo', 'stateholiday', 'schoolholiday'
        ]

        return df[feature_columns], df['sales']

    def train_model(self, X_train, y_train, params=None):
        if params is None:
            params = {
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'objective': 'reg:squarederror'
            }

        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model, X_test, y_test):
        predictions = model.predict(X_test)
        metrics = {
            'mse': mean_squared_error(y_test, predictions),
            'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
            'mae': mean_absolute_error(y_test, predictions),
            'r2': r2_score(y_test, predictions)
        }
        return metrics, predictions

    def run_experiment(self, df: pd.DataFrame, params=None):
        mlflow.set_experiment(self.experiment_name)

        X, y = self.prepare_features(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        with mlflow.start_run() as run:
            if params:
                mlflow.log_params(params)

            model = self.train_model(X_train, y_train, params)
            metrics, predictions = self.evaluate_model(model, X_test, y_test)

            mlflow.log_metrics(metrics)
            # mlflow.xgboost.log_model(model, "model")
            mlflow.xgboost.log_model(model, artifact_path="model")


            logger.info(f"Experiment completed. Run ID: {run.info.run_id}")
            logger.info(f"Metrics: {metrics}")

            return run.info.run_id, metrics, model
