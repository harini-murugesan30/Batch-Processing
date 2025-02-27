from flask import Flask, jsonify
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, TimestampType, LongType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TweetAPI") \
    .getOrCreate()

logging.info("✅ Spark session initialized successfully.")

# Define the schema for the Parquet files
schema = StructType([
    StructField("window", StructType([
        StructField("start", TimestampType(), True),
        StructField("end", TimestampType(), True)
    ]), True),
    StructField("tweet_count", LongType(), True)
])

@app.route('/')
def get_time_series():
    try:
        # Read Time-Series Analysis results from HDFS
        logging.info("📂 Reading Time-Series Analysis results from HDFS...")
        df = spark.read.schema(schema).parquet("hdfs://hdfs:8020/user/spark/output")
        logging.info(f"✅ Successfully read {df.count()} records from HDFS.")
        
        # Convert to Pandas DataFrame and then to JSON
        result = df.toPandas().to_dict(orient="records")
        return jsonify(result)
    except Exception as e:
        logging.error(f"🚨 Error reading Time-Series Analysis results: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)