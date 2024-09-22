# RomanoBot

## Running locally using Docker

(Mostly taken from this [tutorial](https://bytemedirk.medium.com/setting-up-an-hdfs-cluster-with-docker-compose-a-step-by-step-guide-4541cd15b168).)

1. Check that you have Docker installed and started.
2. Navigate to the `hdfs-docker-cluster/` folder and run `docker-compose up --build`. This will start the HDFS service - a name node and a data node + a client running a Jupyter notebook.
3. The web interface for the HDFS service can be accessed at `http://localhost:9870`. You can check the status of the HDFS service there, the files stored, etc.
4. The services can be stop using `docker-compose down`.

## (TODO:) Running with a deployed cluster/service

Can be run the same as locally, but the config file (`hdfs-docker-cluster/hadoop_config/.hdfs_config`) need to be updated to point to the correct cluster/service.

