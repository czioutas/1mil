import os
import sys
import platform
import logging
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors import FlinkKafkaConsumer, JdbcSink, JdbcConnectionOptions
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.table import Row
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        jar_files = [
            "file:///opt/flink/app/lib/flink-connector-kafka-1.17.0.jar",
            "file:///opt/flink/app/lib/kafka-clients-3.2.3.jar",
            "file:///opt/flink/app/lib/flink-connector-jdbc-3.1.0-1.17.jar",
            "file:///opt/flink/app/lib/postgresql-42.6.0.jar"
        ]

        logger.info(f"Listing contents of /opt/flink/app/lib/")
        for root, dirs, files in os.walk('/opt/flink/app/lib/'):
            for file in files:
                logger.info(f"Found file: {file}")
        
        # Ensure you're using the correct file URL for the JARs
        jar_paths = [f"file://{jar}" for jar in jar_files]
        for path in jar_paths:
            logger.info(f"Adding JAR to Flink classpath: {path}")

        env = StreamExecutionEnvironment.get_execution_environment()

        # Add JARs explicitly to the Flink environment
        env.add_jars(*jar_paths)
        logger.info("JARs added successfully")

        # Create the Flink StreamExecutionEnvironment
        env.set_parallelism(1)  # Set parallelism to 1 for simplicity

        # Kafka consumer configuration
        kafka_consumer = FlinkKafkaConsumer(
            topics='emissions',
            deserialization_schema=SimpleStringSchema(),
            properties={
                'bootstrap.servers': 'kafka:9092',  # Kafka server address
                'group.id': 'flink-consumer-group',  # Consumer group ID
                'auto.offset.reset': 'earliest'  # Start from the earliest message
            }
        )

        # Add Kafka source to Flink environment
        kafka_stream = env.add_source(kafka_consumer).name("Kafka Source")

        # Log each Kafka message to verify that data is being received by Flink
        kafka_stream = kafka_stream.map(lambda msg: (logger.info(f"Received message: {msg}"), msg)[1]).name("Log Messages")

        # Print the incoming messages to stdout for verification
        kafka_stream.print()

        # Execute the job
        logger.info("Starting Flink job...")
        env.execute("Minimal Kafka Consumer Job")

    except Exception as e:
        logger.error(f"Error running Flink job: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
