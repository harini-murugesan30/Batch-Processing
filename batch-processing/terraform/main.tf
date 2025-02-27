# Define the Docker provider
provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Create a Docker network
resource "docker_network" "data_pipeline_network" {
  name = "data_pipeline_network"
}

# Define the HDFS container
resource "docker_container" "hdfs" {
  name  = "hdfs"
  image = "bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8"
  hostname = "hdfs"
  env = [
    "CORE_CONF_fs_defaultFS=hdfs://hdfs:8020",
    "HDFS_CONF_dfs_namenode_datanode_registration_ip___hostname___check=false",
    "CLUSTER_NAME=hadoop-cluster"
  ]
  ports {
    internal = 9870
    external = 9870
  }
  ports {
    internal = 9000
    external = 9000
  }
  volumes {
    host_path      = "/path/to/hdfs_namenode"
    container_path = "/hadoop/dfs/name"
  }
  volumes {
    host_path      = "/path/to/hdfs_datanode"
    container_path = "/hadoop/dfs/data"
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  mem_limit = "2g"
  cpus      = 1
}

# Define the Zookeeper container
resource "docker_container" "zookeeper" {
  name  = "zookeeper"
  image = "wurstmeister/zookeeper:latest"
  ports {
    internal = 2181
    external = 2181
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
}

# Define the Kafka container
resource "docker_container" "kafka" {
  name  = "kafka"
  image = "wurstmeister/kafka:latest"
  env = [
    "KAFKA_BROKER_ID=1",
    "KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092",
    "KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092",
    "KAFKA_LOG_RETENTION_HOURS=168",
    "KAFKA_LOG_RETENTION_BYTES=1073741824",
    "KAFKA_NUM_PARTITIONS=1",
    "KAFKA_AUTO_CREATE_TOPICS_ENABLE=true"
  ]
  ports {
    internal = 9092
    external = 9092
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  depends_on = [docker_container.zookeeper]
  mem_limit = "2g"
  cpus      = 2
}

# Define the Spark container
resource "docker_container" "spark" {
  name  = "spark"
  image = "bitnami/spark:latest"
  env = [
    "SPARK_MASTER_HOST=spark"
  ]
  ports {
    internal = 4040
    external = 4040
  }
  ports {
    internal = 7077
    external = 7077
  }
  volumes {
    host_path      = "/path/to/spark_processor.py"
    container_path = "/app/spark_processor.py"
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  depends_on = [docker_container.hdfs, docker_container.kafka]
  mem_limit = "8g"
  cpus      = 4
}

# Define the Flask API container
resource "docker_container" "flask_api" {
  name  = "flask-api"
  image = "flask-api:latest"
  ports {
    internal = 5000
    external = 5000
  }
  volumes {
    host_path      = "/path/to/flask_api"
    container_path = "/app"
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  depends_on = [docker_container.spark]
  mem_limit = "1g"
  cpus      = 1
}

# Define the Prometheus container
resource "docker_container" "prometheus" {
  name  = "prometheus"
  image = "prom/prometheus:latest"
  ports {
    internal = 9090
    external = 9090
  }
  volumes {
    host_path      = "/path/to/prometheus.yml"
    container_path = "/etc/prometheus/prometheus.yml"
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  mem_limit = "1g"
  cpus      = 1
}

# Define the Grafana container
resource "docker_container" "grafana" {
  name  = "grafana"
  image = "grafana/grafana:latest"
  ports {
    internal = 3000
    external = 3000
  }
  env = [
    "GF_SECURITY_ADMIN_PASSWORD=admin"
  ]
  volumes {
    host_path      = "/path/to/grafana_data"
    container_path = "/var/lib/grafana"
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  mem_limit = "1g"
  cpus      = 1
}

# Define the Kafka Producer container
resource "docker_container" "kafka_producer" {
  name  = "kafka-producer"
  image = "kafka-producer:latest"
  env = [
    "KAFKA_SERVER=kafka:9092",
    "KAGGLE_USERNAME=${var.kaggle_username}",
    "KAGGLE_KEY=${var.kaggle_key}"
  ]
  volumes {
    host_path      = "/path/to/kafka_producer"
    container_path = "/app"
  }
  volumes {
    host_path      = "/path/to/kaggle"
    container_path = "/root/.config/kaggle"
  }
  networks_advanced {
    name = docker_network.data_pipeline_network.name
  }
  depends_on = [docker_container.kafka]
  mem_limit = "2g"
  cpus      = 1
}