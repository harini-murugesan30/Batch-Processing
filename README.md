# Data Engineering Project

This project implements a batch-processing-based data architecture for a machine learning application. The system ingests, stores, preprocesses, and aggregates data for quarterly model updates. It uses Infrastructure as Code (IaC) with Terraform to automate the deployment of Docker containers.

## Components

- Apache Kafka: Handles data ingestion.
- HDFS: Stores raw data.
- Apache Spark: Preprocesses and aggregates data.
- Flask API: Serves processed data to the machine learning application.
- Docker: Containerizes all components for isolated and consistent environments.
- Terraform: Implements Infrastructure as Code (IaC) for reproducible setups.

[Architecture](https://github.com/harini-murugesan30/Batch-Processing/blob/main/Architecture_Diagram.png)

## Dataset

The dataset used is the Sentiment140 dataset (https://www.kaggle.com/datasets/kazanova/sentiment140), containing 1.6 million tweets.

## Setup Instructions

### Prerequisites

1. Docker: Install Docker from https://www.docker.com/get-started.
2. Terraform: Install Terraform from https://www.terraform.io/downloads.html.
3. Kaggle API: Set up Kaggle API credentials (username and key) by following the instructions [here](https://www.kaggle.com/docs/api).

### Step 1: Clone the Repository

   git clone [<your-repository-url>](https://github.com/harini-murugesan30/Batch-Processing)
   cd Batch-Processing

### Step 2:Set Up Environment Variables

1. Create a .env file in the root directory of the project.

   ```bash
   cd terraform

2. Add your Kaggle credentials to the .env file::

   ```bash
   KAGGLE_USERNAME=your_kaggle_username
   KAGGLE_KEY=your_kaggle_key

### Step 3: Start the System

1. Start the Docker containers using Docker Compose:
   
   ```bash
   docker-compose up -d

3. Leave HDFS safe mode:

   ```bash
   docker exec -it hdfs bash -c "hdfs dfsadmin -safemode leave"

5. Clean up the HDFS output directory (if needed):

   ```bash
   ./cleanup.sh

7. Create the HDFS output directory:
   
   ```bash
   docker exec -it hdfs bash
   hdfs dfs -mkdir -p /user/spark/output
   hdfs dfs -chown -R spark:supergroup /user/spark/output
   hdfs dfs -ls /user/spark
   hdfs datanode

### Step 4: Ingest Data Using Kafka

1. Start the Kafka producer to ingest data:

   ```bash
   docker exec -it kafka-producer python kafka_producer.py

### Step 5: Process Data Using Spark

1. Start the Spark job to process and aggregate data:

   ```bash
   docker exec -it spark spark-submit --master local[*] --driver-memory 8g --executor-memory 8g --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /app/spark_processor.py

### Step 6: Serve Processed Data via Flask API

1. Access the Flask API at http://localhost:5000 to view the time-series analysis results.

### Step 7: Monitor the System

1. Spark UI: Monitor the Spark job at http://localhost:4040.
2. Prometheus: Access metrics at http://localhost:9090.
3. Grafana: Visualize metrics at http://localhost:3000.

## Execution Sequence

1. Terminal 1:
   ```bash
   docker-compose up -d
   docker exec -it hdfs bash -c "hdfs dfsadmin -safemode leave"
   ./cleanup.sh
   docker exec -it hdfs bash
   hdfs dfs -mkdir -p /user/spark/output
   hdfs dfs -chown -R spark:supergroup /user/spark/output
   hdfs dfs -ls /user/spark
   hdfs datanode

3. Terminal 2:
   ```bash
   docker exec -it kafka-producer python kafka_producer.py
   docker exec -it spark spark-submit --master local[*] --driver-memory 8g --executor-memory 8g --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /app/spark_processor.py

5. Web Interfaces:
   - Spark UI: http://localhost:4040
   - Flask API: http://localhost:5000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

## Recent Updates

- Terraform Integration: Added Terraform configuration to automate the deployment of Docker containers.
- Time-Series Analysis: Updated the Spark job to perform time-series analysis (tweet counts per hour).
- Flask API: Simplified the Flask API to serve time-series results at http://localhost:5000.

## License

This project is licensed under the MIT License.
