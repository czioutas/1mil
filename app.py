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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"Python Version: {sys.version}")
logger.info(f"Python Executable: {sys.executable}")
logger.info(f"Platform: {platform.platform()}")
logger.info(f"Architecture: {platform.machine()}")

# Version checking
try:
    import pyflink
    logger.info("PyFlink imported successfully")
    
    # Alternative version checking methods
    try:
        import apache_beam
        logger.info(f"Apache Beam Version: {apache_beam.__version__}")
    except ImportError:
        logger.warning("Apache Beam not found")

    # This hangs    
    # # Check Flink version through other means
    # try:
    #     from pyflink.datastream import StreamExecutionEnvironment
    #     env = StreamExecutionEnvironment.get_execution_environment()
    #     logger.info("Successfully created Flink StreamExecutionEnvironment")
    # except Exception as e:
    #     logger.error(f"Error creating Flink environment: {e}")
    #     raise

except ImportError as e:
    logger.error(f"Failed to import PyFlink: {e}")
    raise


def parse_event(value: str) -> Row:
    """
    Parse incoming Kafka event to extract required fields.
    Ensures proper type conversion for all fields.
    """
    try:
        logger.info(f"Raw Kafka message: {value}")
        event = json.loads(value)
        logger.info(f"Parsed JSON: {event}")
        
        organization_id = int(event.get('organizationId', 0))
        emission_value = float(event.get('value', 0.0))
        
        logger.info(f"Converted values - org_id: {organization_id}, value: {emission_value}")
        
        return Row(organization_id, datetime.now().strftime("%Y-%m"), emission_value)
    except Exception as e:
        logger.error(f"Detailed parsing error: {e}")
        logger.error(f"Problematic input: {value}")
        return Row(0, datetime.now().strftime("%Y-%m"), 0.0)

def aggregate_emissions():
    try:
        # Check if JARs exist
        jar_files = [
            "/opt/flink/app/lib/flink-connector-kafka-1.17.0.jar",
            "/opt/flink/app/lib/kafka-clients-3.2.3.jar",
            "/opt/flink/app/lib/flink-connector-jdbc-3.1.0-1.17.jar",
            "/opt/flink/app/lib/postgresql-42.6.0.jar"
        ]
        
        for jar in jar_files:
            logger.info(f"Checking JAR: {jar}")
            if os.path.exists(jar):
                # Check file permissions and readability
                try:
                    with open(jar, 'rb') as f:
                        # Try to read the first few bytes
                        f.read(10)
                    logger.info(f"JAR is readable: {jar}")
                except PermissionError:
                    logger.error(f"Permission denied reading JAR: {jar}")
                    raise
                except IOError as e:
                    logger.error(f"Error reading JAR {jar}: {e}")
                    raise
            else:
                logger.error(f"JAR file does not exist: {jar}")
                raise FileNotFoundError(f"Required JAR not found: {jar}")

        logger.info("All JARs verified successfully")

        logger.info("Creating StreamExecutionEnvironment")
        env = StreamExecutionEnvironment.get_execution_environment()
        logger.info(f"Environment created: {env}")
        
        logger.info("Setting runtime mode to STREAMING")
        try:
            env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
            logger.info("Runtime mode set successfully")
        except Exception as mode_error:
            logger.error(f"Error setting runtime mode: {mode_error}", exc_info=True)
        
        logger.info("Setting parallelism")
        try:
            env.set_parallelism(1)
            logger.info("Parallelism set successfully")
        except Exception as parallelism_error:
            logger.error(f"Error setting parallelism: {parallelism_error}", exc_info=True)
        
        logger.info("Enabling checkpointing")
        try:
            env.enable_checkpointing(60000)  # Checkpoint every 60 seconds
            logger.info("Checkpointing enabled successfully")
        except Exception as checkpoint_error:
            logger.error(f"Error enabling checkpointing: {checkpoint_error}", exc_info=True)

        logger.info("Adding JARs to classpath")
        # Verify JAR paths before adding
        jar_paths = [f"file://{jar}" for jar in jar_files]
        for path in jar_paths:
            logger.info(f"Adding JAR path: {path}")
        
        env.add_jars(*jar_paths)

        logger.info("JAR paths added successfully")

        logger.info("Setting up Kafka consumer...")
        try:
            kafka_consumer = FlinkKafkaConsumer(
                topics='emissions',
                deserialization_schema=SimpleStringSchema(),
                properties={
                    'bootstrap.servers': 'kafka:9092',
                    'group.id': 'flink-consumer-group',
                    'auto.offset.reset': 'earliest'
                }
            )
            logger.info("Kafka consumer created successfully")
            
            kafka_consumer.set_start_from_earliest()
            logger.info("Kafka consumer start position set")
            
        except Exception as kafka_error:
            logger.error(f"Error setting up Kafka consumer: {kafka_error}", exc_info=True)
            raise
        
        logger.info("Adding Kafka source...")
        kafka_stream = env.add_source(kafka_consumer).name("Kafka Source")
        
        # Add a map function to log incoming messages
        kafka_stream = kafka_stream.map(
            lambda x: (logger.info(f"Received message: {x}"), x)[1]
        ).name("Log Messages")

        logger.info("Setting up transformations...")
        # Transform and aggregate emissions data
        parsed_stream = (
            kafka_stream
            .map(
                parse_event,
                output_type=Types.ROW([Types.INT(), Types.STRING(), Types.FLOAT()])
            )
            .name("Parse Kafka Events")
        )

        logger.info("Setting up aggregations...")
        aggregated_stream = (
            parsed_stream
            .key_by(lambda x: (x[0], x[1]))  # Group by organization_id and month
            .reduce(lambda a, b: Row(a[0], a[1], a[2] + b[2]))  # Aggregate emission values
            .name("Aggregate Emissions")
        )

        logger.info("Setting up JDBC connection...")
        # Create JDBC connection options
        jdbc_connection_options = JdbcConnectionOptions.JdbcConnectionOptionsBuilder()\
            .with_url("jdbc:postgresql://postgres:5432/demo")\
            .with_driver_name("org.postgresql.Driver")\
            .with_user_name("demo")\
            .with_password("demo")\
            .build()

        logger.info("Setting up JDBC sink...")
        # Create JDBC sink
        jdbc_sink = JdbcSink.sink(
            sql="""INSERT INTO "AggregatedEmission" ("organizationId", "month", "totalEmissions") 
                VALUES (?, ?, ?) 
                ON CONFLICT ("organizationId", "month") 
                DO UPDATE SET "totalEmissions" = EXCLUDED."totalEmissions";""",
            type_info=Types.ROW([Types.INT(), Types.STRING(), Types.FLOAT()]),
            jdbc_connection_options=jdbc_connection_options
        )

        logger.info("Adding sink to stream...")
        aggregated_stream.add_sink(jdbc_sink).name("PostgreSQL Sink")

        logger.info("Executing job...")
        result = env.execute("Kafka to PostgreSQL - Emissions Aggregator")
        logger.info(f"Job executed successfully: {result}")
        
    except Exception as e:
        logger.error(f"Error in aggregate_emissions: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Starting Flink application...")
    try:
        aggregate_emissions()
    except Exception as e:
        logger.error("Application failed", exc_info=True)
        raise
