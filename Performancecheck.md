# Stress Test

```
curl -X POST http://localhost:3000/load-test \
-H "Content-Type: application/json" \
-d '{"numberOfMessages": 1000000}'
```

Invoke-RestMethod -Uri "http://localhost:3000/load-test" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"numberOfMessages": 1000000}'

## Flink UI

Check "Running Jobs" for:

Overall throughput
Backpressure status
Processing latency
Task manager status
Individual operator metrics

## Kafka

docker exec kafka kafka-consumer-groups \
--bootstrap-server kafka:9092 \
--describe \
--group flink-emissions-group

## Postgres

-- Monitor rate of aggregation updates
SELECT count(*), 
       date_trunc('minute', "timestamp") as minute
FROM "Emission"
GROUP BY minute
ORDER BY minute DESC
LIMIT 5;

-- Check aggregated results
SELECT * 
FROM "AggregatedEmission" 
ORDER BY "month" DESC, "organizationId";