package com.example;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
import org.apache.flink.connector.jdbc.JdbcExecutionOptions;
import org.apache.flink.connector.jdbc.JdbcSink;
import org.json.JSONObject;
import java.time.LocalDate;

public class FlinkEmissionsProcessor {
    public static void main(String[] args) throws Exception {
        // Set up the streaming execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Configure Kafka source
        KafkaSource<String> source = KafkaSource.<String>builder()
                .setBootstrapServers("kafka:9092")
                .setTopics("emissions")
                .setGroupId("flink-emissions-group")
                .setStartingOffsets(OffsetsInitializer.earliest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();

        // Create data stream from Kafka with WatermarkStrategy
        DataStream<String> kafkaStream = env.fromSource(
            source,
            WatermarkStrategy.noWatermarks(),
            "Kafka Source"
        );

        // Process the stream
        DataStream<EmissionRecord> processedStream = kafkaStream
            .map(value -> {
                JSONObject json = new JSONObject(value);
                String currentMonth = LocalDate.now().toString().substring(0, 7); // YYYY-MM
                return new EmissionRecord(
                    json.getInt("organizationId"),
                    currentMonth,
                    json.getDouble("value")
                );
            });

        // Configure JDBC sink
        processedStream.addSink(
            JdbcSink.sink(
                "INSERT INTO public.\"AggregatedEmission\" (\"organizationId\", \"month\", \"totalEmissions\") " +
                "VALUES (?, ?, ?) " +
                "ON CONFLICT (\"organizationId\", \"month\") " +
                "DO UPDATE SET \"totalEmissions\" = \"AggregatedEmission\".\"totalEmissions\" + EXCLUDED.\"totalEmissions\"",
                (statement, record) -> {
                    statement.setInt(1, record.organizationId);
                    statement.setString(2, record.month);
                    statement.setDouble(3, record.value);
                },
                JdbcExecutionOptions.builder()
                    .withBatchSize(1000)
                    .withBatchIntervalMs(200)
                    .withMaxRetries(5)
                    .build(),
                new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
                    .withUrl("jdbc:postgresql://postgres:5432/demo")
                    .withDriverName("org.postgresql.Driver")
                    .withUsername("demo")
                    .withPassword("demo")
                    .build()
            )
        );

        // Execute the job
        env.execute("Emissions Processor");
    }

    // Record class to hold emission data
    public static class EmissionRecord {
        public final int organizationId;
        public final String month;
        public final double value;

        public EmissionRecord(int organizationId, String month, double value) {
            this.organizationId = organizationId;
            this.month = month;
            this.value = value;
        }
    }
}