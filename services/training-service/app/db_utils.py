import os
from sqlalchemy import create_engine
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine(
            f"postgresql://postgres:{os.getenv('MAIN_DB_PW')}@postgres:{os.getenv('POSTGRES_PORT')}/postgres"
        )

    def connect(self):
        try:
            self.engine.connect()
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise

    def get_sales_data(self, store=None, start_date=None, end_date=None):
        query = "SELECT * FROM rossman_sales WHERE 1=1"
        if store:
            query += f" AND store = {store}"
        if start_date:
            query += f" AND date >= '{start_date}'"
        if end_date:
            query += f" AND date <= '{end_date}'"
        return pd.read_sql(query, self.engine)
