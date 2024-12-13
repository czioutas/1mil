# Real-time Emissions Processing System

This project implements a real-time data processing pipeline for emissions data using Kafka, Flink, and PostgreSQL.

## System Architecture

The system consists of several components working together:

1. **Node.js API** - Receives emission events and sends them to Kafka
2. **Apache Kafka** - Message broker for event streaming
3. **Apache Flink** - Stream processing engine for real-time aggregations
4. **PostgreSQL** - Persistent storage for raw and aggregated data

## Components Description

### Apache Kafka & ZooKeeper
- **ZooKeeper**: Manages Kafka cluster state and configurations
- **Kafka**: Message broker that handles the emission events stream
- **Kafka UI**: Web interface for monitoring Kafka topics and messages

### Apache Flink
- **Job Manager**: Coordinates the distributed processing
- **Task Manager**: Executes the actual data processing tasks
- **Flink App**: Python application that processes the emission events

### Data Storage
- **PostgreSQL**: Stores both raw emissions data and aggregated results

### API Application
- **Node.js API**: REST API for submitting emission events
- Writes to both Kafka and PostgreSQL
- Enables data ingestion into the system

## Startup Order

The correct order to start the services is:

1. ZooKeeper (required by Kafka)
2. Kafka (message broker)
3. PostgreSQL (database)
4. Node.js API (data ingestion)
5. Flink Job Manager (processing coordinator)
6. Flink Task Manager (processing worker)
7. Flink Application (processing logic)

```bash
# Start core services
docker-compose up -d zookeeper kafka kafka-ui postgres

# Wait a moment for Kafka to be ready, then start the API
docker-compose up -d app

# Start Flink services
docker-compose up -d flink-jobmanager
docker-compose up -d flink-taskmanager
docker-compose up -d flink-app
```

## Service Endpoints

| Service          | URL                    | Description                     |
|-----------------|------------------------|---------------------------------|
| Node.js API     | http://localhost:3000  | REST API for emission events   |
| Kafka UI        | http://localhost:8080  | Kafka monitoring interface     |
| Flink Dashboard | http://localhost:8081  | Flink jobs monitoring         |
| PostgreSQL      | localhost:5434         | Database (external port)       |

## API Endpoints

| Method | Endpoint     | Description          | Example Payload                               |
|--------|-------------|---------------------|----------------------------------------------|
| POST   | /emissions  | Submit emission     | `{"organizationId": 1, "value": 100}`       |

## Useful Commands

### Docker Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f app
docker-compose logs -f flink-app

# Restart specific service
docker-compose restart app
```

### Kafka Commands
```bash
# Create topic
docker exec kafka kafka-topics --create --topic emissions --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1

# List topics
docker exec kafka kafka-topics --list --bootstrap-server kafka:9092

# Describe topic
docker exec kafka kafka-topics --describe --topic emissions --bootstrap-server kafka:9092
```

### Database Commands
```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U demo -d demo

# Common PostgreSQL queries
SELECT * FROM emission ORDER BY timestamp DESC LIMIT 5;
SELECT * FROM aggregated_emission ORDER BY month DESC;
```

### Testing
```powershell
# Send test emission (PowerShell)
Invoke-WebRequest -Method POST -Uri http://localhost:3000/emissions `
-Headers @{"Content-Type"="application/json"} `
-Body '{"organizationId": 1, "value": 100}'
```
```bash
# Send test emission (bash/curl)
curl -X POST http://localhost:3000/emissions \
-H "Content-Type: application/json" \
-d '{"organizationId": 1, "value": 100}'
```

## Data Flow

1. Emission event is sent to API endpoint
2. API writes to both:
   - Kafka topic 'emissions'
   - PostgreSQL raw emissions table
3. Flink application:
   - Reads from Kafka topic
   - Aggregates emissions by organization and month
   - Writes aggregates to PostgreSQL
4. Results can be queried from PostgreSQL tables:
   - `emission` - raw events
   - `aggregated_emission` - monthly aggregates

## Monitoring

1. **Kafka UI** (http://localhost:8080):
   - Monitor topics
   - View messages
   - Check cluster health

2. **Flink Dashboard** (http://localhost:8081):
   - Monitor jobs
   - View processing metrics
   - Check task manager status

## Troubleshooting

1. **Kafka Connection Issues**
   - Verify ZooKeeper is running
   - Check Kafka logs: `docker-compose logs kafka`
   - Ensure topics are created properly

2. **Flink Job Issues**
   - Check Job Manager UI for errors
   - View Flink app logs: `docker-compose logs flink-app`
   - Verify task managers are registered

3. **Database Issues**
   - Verify PostgreSQL is running
   - Check connection string in app environment
   - View database logs: `docker-compose logs postgres`