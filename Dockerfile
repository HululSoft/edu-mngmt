# Use the official Python image
FROM python:3.12-slim

ENV PG_CONFIG=/usr/bin/pg_config

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY src /app


COPY gunicorn.conf.py /app

# Copy the entrypoint script to the container
COPY entrypoint.sh entrypoint.sh

# Ensure the entrypoint script has execute permissions
RUN chmod +x entrypoint.sh

# Install build dependencies for psycopg2 pip package install from resource 
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
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
