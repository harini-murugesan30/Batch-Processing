# Use a base image with Java pre-installed
FROM bitnami/spark:3.5.0

# Set JAVA_HOME
ENV JAVA_HOME=/opt/bitnami/java

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "app.py"]