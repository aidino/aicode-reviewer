FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY src/webapp/frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend application
COPY src/webapp/frontend/ .

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 5173

# Command to run the application in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 