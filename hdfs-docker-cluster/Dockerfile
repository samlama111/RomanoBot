# Use an appropriate base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the script that is to be run
COPY hdfs_test.py .
# Copy config
COPY ./hdfs-docker-cluster/hadoop_config/.hdfscli.cfg ./hdfs-docker-cluster/hadoop_config/.hdfscli.cfg
# Copy the data
COPY ./data/ ./data/

# Set the entrypoint to run your script
ENTRYPOINT ["python", "hdfs_test.py"]