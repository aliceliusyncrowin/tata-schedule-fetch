from azure.storage.blob import BlobServiceClient
import os
import json

AZURE_STORAGE_ACCOUNT_CONNECTION_STRING = os.environ["AZURE_STORAGE_ACCOUNT_CONNECTION_STRING"]

# Create BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_ACCOUNT_CONNECTION_STRING)

# TODO: determine blob service client + container name, if needed create new
def get_solcast_blob_client(blob_name: str):
    blob_client = blob_service_client.get_blob_client(container="tata-schedule", blob=blob_name)
    return blob_client


def upload_solcast_to_blob(blob_name: str, data: bytes):
    blob_client = get_solcast_blob_client(blob_name)
    blob_client.upload_blob(data)

def save_schedule_to_blob(data: dict, date: str, now: str):
    blob_name = f"{date}/retrieved_{now}.json"
    data_bytes = json.dumps(data).encode('utf-8')
    upload_solcast_to_blob(blob_name, data_bytes)