-- CreateTable
BEGIN;

-- First drop the existing table if it exists
DROP TABLE IF EXISTS "AggregatedEmission";

-- Create the new partitioned table
CREATE TABLE "AggregatedEmission" (
    "organizationId" INTEGER NOT NULL,
    "month" TEXT NOT NULL,
    "totalEmissions" DOUBLE PRECISION NOT NULL,
    CONSTRAINT "AggregatedEmission_pkey" PRIMARY KEY ("organizationId", "month")
) PARTITION BY LIST ("organizationId");

-- Create the partitions
CREATE TABLE "AggregatedEmission_1" PARTITION OF "AggregatedEmission"
    FOR VALUES IN (1);

CREATE TABLE "AggregatedEmission_2" PARTITION OF "AggregatedEmission"
    FOR VALUES IN (2);

CREATE TABLE "AggregatedEmission_3" PARTITION OF "AggregatedEmission"
    FOR VALUES IN (3);

COMMIT;