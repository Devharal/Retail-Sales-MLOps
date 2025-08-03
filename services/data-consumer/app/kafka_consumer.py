import json
import logging
from kafka import KafkaConsumer
from db_utils import DatabaseConnection
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SalesDataConsumer:
    def __init__(self):
        self.topic = "sale_rossman_store"
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='sales_consumer_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.db = DatabaseConnection()
        self.db.connect()

    def process_message(self, message):
        try:
            df = pd.DataFrame([message])
            df.to_sql('rossman_sales', self.db.engine, if_exists='append', index=False)
            logger.info(f"Saved store {message.get('store')}")
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")

    def start_consuming(self):
        logger.info("Starting consumer ...")
        try:
            for message in self.consumer:
                self.process_message(message.value)
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}")
            raise

if __name__ == "__main__":
    consumer = SalesDataConsumer()
    consumer.start_consuming()
