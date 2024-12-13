-- CreateTable
CREATE TABLE "Organization" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Organization_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Emission" (
    "id" SERIAL NOT NULL,
    "organizationId" INTEGER NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "value" DOUBLE PRECISION NOT NULL,

    CONSTRAINT "Emission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AggregatedEmission" (
    "organizationId" INTEGER NOT NULL,
    "month" TEXT NOT NULL,
    "totalEmissions" DOUBLE PRECISION NOT NULL,

    CONSTRAINT "AggregatedEmission_pkey" PRIMARY KEY ("organizationId","month")
);

-- AddForeignKey
ALTER TABLE "Emission" ADD CONSTRAINT "Emission_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "Organization"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
