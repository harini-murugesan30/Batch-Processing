from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, current_timestamp
from pyspark.sql.types import StringType, StructType, StructField
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kafka and HDFS Configuration
KAFKA_TOPIC = "tweets"
KAFKA_SERVER = "kafka:9092"
HDFS_PATH = "hdfs://hdfs:8020/user/spark/output"

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.shuffle.partitions", "16") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

logging.info("✅ Spark session initialized successfully.")

# Define Schema for incoming Kafka messages
schema = StructType([
    StructField("text", StringType(), True),
    StructField("sentiment", StringType(), True)
])

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

logging.info("✅ Successfully connected to Kafka.")

# Convert Kafka data from JSON
tweets = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", current_timestamp())

# Time-Series Analysis: Count tweets per hour
tweet_counts = tweets \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(
        window(col("timestamp"), "1 hour")  # 1-hour window
    ) \
    .count() \
    .withColumnRenamed("count", "tweet_count")

# Write output to HDFS in Parquet format
query = tweet_counts.writeStream \
    .format("parquet") \
    .option("path", HDFS_PATH) \
    .option("checkpointLocation", "/tmp/spark-checkpoint") \
    .outputMode("append") \
    .start()

logging.info("✅ Spark streaming query started successfully.")
query.awaitTermination()