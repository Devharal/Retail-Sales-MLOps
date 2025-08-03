import os
import time
import logging
import pandas as pd
import json
from datetime import datetime
from kafka import KafkaProducer

# Setup logger
logger = logging.getLogger("kafka_producer")
logger.setLevel(logging.INFO)

# Environment variables
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sale_rossman_store")
KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "kafka:9092")

# Preprocess input data
def preprocess_input_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = map(str.lower, df.columns)
    df["stateholiday"] = df["stateholiday"].astype(str)
    df["productname"] = "product_A"
    df = df.sort_values("date").reset_index(drop=True)
    return df

# Main producer loop
def main():
    sale_stream = pd.read_csv("datasets/train_only_last_10d.csv")
    sale_stream = preprocess_input_df(sale_stream)

    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )

    pointer = 0
    while True:
        if pointer == len(sale_stream):
            pointer = 0

        row = sale_stream.iloc[pointer]
        row["date"] = datetime.now().strftime("%Y-%m-%d")
        sale = json.loads(row.to_json())

        logger.info(f"Sent: {sale}")
        producer.send(topic=KAFKA_TOPIC, value=sale)
        producer.flush()

        pointer += 1
        time.sleep(10)

# Run main
if __name__ == "__main__":
    main()
