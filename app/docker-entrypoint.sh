#!/bin/sh

# Run Prisma migrations
npx prisma migrate dev

# Start the Node.js app
exec "$@"
