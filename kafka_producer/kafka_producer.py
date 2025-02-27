import os
import json
import time
import kaggle
from kafka import KafkaProducer
import pandas as pd
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv

DATASET_PATH = "./data/training.1600000.processed.noemoticon.csv"
KAFKA_TOPIC = "tweets"
KAFKA_SERVER = "kafka:9092" 

# Load environment variables from .env file
load_dotenv()

# Set Kaggle credentials from environment variables
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

def download_dataset():
    """Downloads dataset if not already present"""
    if not os.path.exists(DATASET_PATH):
        print("📥 Downloading dataset...")
        os.makedirs("./data", exist_ok=True)
        os.system("kaggle datasets download -d kazanova/sentiment140 -p ./data --unzip")
    else:
        print("✅ Dataset already exists. Skipping download.")

def wait_for_kafka():
    """Wait for Kafka to be ready"""
    retries = 10
    for i in range(retries):
        try:
            producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
            producer.close()
            print("✅ Kafka is ready!")
            return
        except NoBrokersAvailable:
            print(f"⏳ Waiting for Kafka... Attempt {i+1}/{retries}")
            time.sleep(5)
    raise Exception("🚨 Kafka not available after multiple retries!")

def send_to_kafka():
    """Sends data to Kafka in batches"""
    wait_for_kafka()
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        batch_size=65536,  # Increased batch size for efficiency
        linger_ms=50  # Reduce delay for better batching
    )

    df = pd.read_csv(DATASET_PATH, encoding="ISO-8859-1", nrows=1000000)

    batch_size = 100000  # Process messages in batches
    messages = []
    for index, row in df.iterrows():
        message = {"text": str(row.iloc[5]), "sentiment": str(row.iloc[0])}
        future = producer.send(KAFKA_TOPIC, value=message)
        messages.append(future)

        # Flush every 100000 messages for performance
        if len(messages) % batch_size == 0:
            for msg in messages:
                msg.get(timeout=10)  # Ensure message is delivered
            producer.flush()
            messages = []
            print(f"✅ Sent {index+1} messages to Kafka")

    # Final flush
    for msg in messages:
        msg.get(timeout=10)
    producer.flush()
    print("✅ Finished sending all messages to Kafka!")

# Run functions
download_dataset()
send_to_kafka()