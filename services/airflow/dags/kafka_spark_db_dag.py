from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def create_spark_session():
    """Create Spark session"""
    return SparkSession.builder \
        .appName("KafkaSparkStreaming") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()

def process_kafka_stream():
    """Process Kafka stream and save to PostgreSQL"""
    spark = create_spark_session()
    
    # Define schema for sales data
    schema = StructType([
        StructField("store", IntegerType()),
        StructField("date", StringType()),
        StructField("sales", FloatType()),
        StructField("customers", IntegerType()),
        StructField("open", IntegerType()),
        StructField("promo", IntegerType()),
        StructField("stateholiday", StringType()),
        StructField("schoolholiday", IntegerType())
    ])
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", os.getenv("KAFKA_TOPIC")) \
        .load()
    
    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")
    
    # Write to PostgreSQL
    query = parsed_df \
        .writeStream \
        .outputMode("append") \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://postgres:{os.getenv('POSTGRES_PORT')}/postgres") \
        .option("dbtable", os.getenv("SALES_TABLE_NAME")) \
        .option("user", "postgres") \
        .option("password", os.getenv("MAIN_DB_PW")) \
        .option("checkpointLocation", os.getenv("SPARK_STREAM_CHECKPOINTS_PATH")) \
        .start()
    
    query.awaitTermination()

with DAG(
    'kafka_spark_db',
    default_args=default_args,
    description='Stream sales data from Kafka to PostgreSQL using Spark',
    schedule_interval='@continuous',  # Run continuously
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['streaming']
) as dag:
    
    stream_processor = PythonOperator(
        task_id='process_kafka_stream',
        python_callable=process_kafka_stream
    )


# from datetime import datetime, timedelta
# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from pyspark.sql import SparkSession
# import logging
# from db_utils import DatabaseConnection

# logger = logging.getLogger(__name__)

# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# def stream_kafka_to_postgres():
#     """Stream data from Kafka to PostgreSQL using Spark"""
#     spark = SparkSession.builder \
#         .appName("KafkaToPostgres") \
#         .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2") \
#         .getOrCreate()
    
#     try:
#         # Read from Kafka
#         df = spark \
#             .readStream \
#             .format("kafka") \
#             .option("kafka.bootstrap.servers", "kafka:9092") \
#             .option("subscribe", "sale_rossman_store") \
#             .load()
        
#         # Assuming value is JSON string
#         df = df.selectExpr("CAST(value AS STRING) as json") \
#                .select(from_json("json", "store INT, date STRING, sales FLOAT, customers INT, promo INT, schoolholiday INT").alias("data")) \
#                .select("data.*")
        
#         # Write to PostgreSQL
#         def write_to_postgres(batch_df, batch_id):
#             db = DatabaseConnection()
#             batch_df.toPandas().to_sql('rossman_sales', db.engine, if_exists='append', index=False)
#             logger.info(f"Batch {batch_id} written to PostgreSQL")
        
#         query = df \
#             .writeStream \
#             .foreachBatch(write_to_postgres) \
#             .outputMode("append") \
#             .start()
        
#         query.awaitTermination(timeout=300)  # Run for 5 minutes per task execution
#         spark.stop()
#     except Exception as e:
#         logger.error(f"Streaming failed: {str(e)}")
#         spark.stop()
#         raise

# with DAG(
#     'kafka_to_postgres',
#     default_args=default_args,
#     description='DAG to stream Kafka data to PostgreSQL',
#     schedule_interval=timedelta(minutes=10),
#     start_date=datetime(2025, 7, 1),
#     catchup=False,
# ) as dag:
#     stream_task = PythonOperator(
#         task_id='stream_kafka_to_postgres',
#         python_callable=stream_kafka_to_postgres,
#     )