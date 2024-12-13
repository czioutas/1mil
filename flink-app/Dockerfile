# Build stage
FROM maven:3.8.4-openjdk-11 AS builder

# Set working directory
WORKDIR /build

# Copy the POM file
COPY pom.xml .

# Copy source code
COPY src ./src/

# Build the application
RUN mvn clean package

# Runtime stage
FROM flink:1.17.0-java11

# Copy the built artifact from builder stage
COPY --from=builder /build/target/flink-emissions-processor-1.0-SNAPSHOT.jar /opt/flink/usrlib/flink-emissions-processor.jar

# Add any additional configuration if needed
COPY log4j.properties /opt/flink/conf/

# Set environment variables
ENV FLINK_PROPERTIES="jobmanager.rpc.address: flink-jobmanager"

# Command to run the application
CMD ["standalone-job", "--job-classname", "com.example.FlinkEmissionsProcessor", "--jar", "/opt/flink/usrlib/flink-emissions-processor.jar"]