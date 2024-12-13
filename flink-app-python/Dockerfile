FROM flink:1.17.0

WORKDIR /opt/flink/app

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    openjdk-11-jdk \
    wget && \
    # Create symlink for python to python3
    ln -sf /usr/bin/python3 /usr/bin/python && \
    # Clean up apt cache
    rm -rf /var/lib/apt/lists/*

# Create symlink for Java includes
RUN mkdir -p /opt/java/openjdk/include && \
    ln -s /usr/lib/jvm/java-11-openjdk-arm64/include/* /opt/java/openjdk/include/

# Download required JARs
RUN wget -P /opt/flink/app/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-kafka/1.17.0/flink-connector-kafka-1.17.0.jar && \
    wget -P /opt/flink/app/lib/ https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/3.2.3/kafka-clients-3.2.3.jar && \
    wget -P /opt/flink/app/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc/3.1.0-1.17/flink-connector-jdbc-3.1.0-1.17.jar && \
    wget -P /opt/flink/app/lib/ https://jdbc.postgresql.org/download/postgresql-42.6.0.jar

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/opt/flink/app"
ENV PYTHON_HOME "/usr/bin/python3"

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your application
COPY . .

CMD ["python3", "app.py"]