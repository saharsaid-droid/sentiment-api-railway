import os
from azure.storage.blob import BlobServiceClient
import tarfile

# اقرئي سلسلة الاتصال من متغيرات البيئة
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not connect_str:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable not set.")

CONTAINER_NAME = "model"
# !!! هام جداً: غيري هذا الاسم ليطابق اسم ملف الموديل في Azure
MODEL_TAR_BLOB_NAME = "my_sentiment_model.tar.gz"
DOWNLOAD_PATH = os.path.join("/app", MODEL_TAR_BLOB_NAME)
EXTRACT_PATH = "/app/model"


def download_and_extract_model():
    """Downloads and extracts the model from Azure Blob Storage."""
    print("--- Starting Model Download and Extraction ---")
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=MODEL_TAR_BLOB_NAME
        )

        print(f"Downloading {MODEL_TAR_BLOB_NAME} to {DOWNLOAD_PATH}...")
        with open(DOWNLOAD_PATH, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print("Download complete.")

        print(f"Extracting {DOWNLOAD_PATH} to {EXTRACT_PATH}...")
        os.makedirs(EXTRACT_PATH, exist_ok=True)
        with tarfile.open(DOWNLOAD_PATH, "r:gz") as tar:
            tar.extractall(path=EXTRACT_PATH)
        print("Extraction complete.")

        os.remove(DOWNLOAD_PATH)
        print(f"Removed {DOWNLOAD_PATH}.")
        print("--- Model is ready! ---")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    download_and_extract_model()
