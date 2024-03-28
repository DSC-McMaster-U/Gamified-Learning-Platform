# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available
EXPOSE 8080

# Define environment variable for the port (optional)
ENV PORT 8080

# Run the application (using "shell" form)
CMD cd app ; flask --app run_app.py run --host=0.0.0.0 --port=8080