# Use the official Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY src /app


COPY gunicorn.conf.py /app

# Copy the entrypoint script to the container
COPY entrypoint.sh entrypoint.sh

# Ensure the entrypoint script has execute permissions
RUN chmod +x entrypoint.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Declare the data folder as a volume
VOLUME /app/data
RUN chmod +x entrypoint.sh
RUN ls /app/
# Set the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
