# Use Debian-based Node.js image
FROM node:18

# Set working directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy Prisma schema
COPY prisma ./prisma/

# Generate Prisma client
RUN npx prisma generate

# Copy the rest of the source code
COPY . .

# Expose the application port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]