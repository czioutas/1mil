# PGSQL Parititon

EXPLAIN ANALYZE 
SELECT * FROM "AggregatedEmission" 
WHERE "organizationId" = 1 
  AND "month" >= '2024-01';