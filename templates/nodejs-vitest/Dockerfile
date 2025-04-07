# Use an official Node runtime as a parent image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the app (if applicable, e.g., for production)
# RUN npm run build

# Make port 5173 available (default Vite port)
EXPOSE 5173

# Run the app when the container launches
CMD ["npm", "run", "dev", "--", "--host"]