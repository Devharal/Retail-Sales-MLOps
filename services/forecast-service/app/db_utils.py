import os
import logging
from sqlalchemy import create_engine
import pandas as pd

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.user = "postgres"
        self.password = os.getenv("MAIN_DB_PW")
        self.host = "postgres"
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.database = "postgres"
        self.engine = None

    def get_connection_string(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self):
        try:
            self.engine = create_engine(self.get_connection_string())
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise

    def save_predictions(self, predictions_df):
        try:
            predictions_df.to_sql('forecast_results', self.engine, if_exists='append', index=False)
            logger.info(f"Saved {len(predictions_df)} predictions")
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")
            raise
