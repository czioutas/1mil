#!/bin/bash

until /usr/bin/kafka-topics --bootstrap-server kafka:9092 --list; do
  echo "Waiting for Kafka to be ready..."
  sleep 5
done

# Create the emissions topic
kafka-topics \
  --create \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic emissions || echo "Topic already exists"



