# Use the official Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the source code to the container
COPY src /app

# Copy the default data folder into the container
COPY src/data /default-data

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Declare the data folder as a volume
VOLUME /app/data

# Add an entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script to initialize data and run the app
ENTRYPOINT ["./entrypoint.sh"]

# Command to run the application
CMD ["python", "app.py"]
