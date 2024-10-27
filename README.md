# RomanoBot

## Running locally using Docker

EDIT we followed another tutorial but this was still a good starting point -> (Mostly taken from this [tutorial](https://bytemedirk.medium.com/setting-up-an-hdfs-cluster-with-docker-compose-a-step-by-step-guide-4541cd15b168).)

1. Check that you have Docker installed and started.
2. Run `docker-compose up --build`. This will start the HDFS service - a name node and two data nodes + a client running a Jupyter notebook
   2.1 The reason to have a dedicated jupyter notebook client is to be able to communicate with the name and datanodes in the same docker network
   2.1.1 Data used for training should be uploaded into jupyter/volumes/data/_data_file_name_.csv
   2.2 It is important to set the right environment variables for the name and datanode so that they can communicate and find each other ([syntax for config to env conversion](https://github.com/s22s/hadoop-docker))
3. The web interface for the HDFS service can be accessed at `http://localhost:9870`. You can check the status of the HDFS service there, the files stored, etc.
4. The ray dashboard can be accessed at `http://localhost:8265`
5. The Notebook can be accessed at `http://localhost:8888`
6. The services can be stopped using `docker-compose down`.

Note: In order to run the frontend successfully the model needs to be generated beforehand. In the case where the model does not exist yet it should be trained first and after that
the frontend can be spun up using `docker-compose up flask --build` to specifically spin up the front-end.
