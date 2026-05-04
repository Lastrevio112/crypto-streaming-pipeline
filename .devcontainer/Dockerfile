FROM --platform=linux/arm64 apache/flink:2.0.0-scala_2.12-java21 AS flink

FROM --platform=linux/arm64 python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Copy the Kafka connector JAR from the Flink image into the app container
COPY --from=flink /opt/flink/lib/flink-sql-connector-kafka-*.jar /opt/flink-jars/

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64

RUN pip install jep

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN wget -P /usr/local/lib/python3.11/site-packages/pyflink/lib/ \
    https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/4.0.1-2.0/flink-sql-connector-kafka-4.0.1-2.0.jar