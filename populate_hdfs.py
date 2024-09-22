from hdfs import Config

client = Config(path="./hdfs-docker-cluster/hadoop_config/.hdfscli.cfg").get_client(
    "dev"
)

print("Existing root-level content :", client.list("/"))

files_to_upload = ["transfers.csv"]

# Check if the file exists
for file in files_to_upload:
    local_path = f"./data/{file}"
    remote_path = f"/tmp/{file}"
    print(f"Checking if {file} exists...")
    if client.status(remote_path, strict=False):
        print(f"{file} exists!")
    else:
        print(f"{file} does not exist!")
        print("Uploading file to /tmp...")
        # Upload a file to tmp, to be processed further
        client.upload(remote_path, local_path)

print("/tmp contents: ", client.list("/tmp"))
