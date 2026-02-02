# Start from the official Airflow image
FROM puckel/docker-airflow:1.10.9

# Copy requirements.txt into the container
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt
