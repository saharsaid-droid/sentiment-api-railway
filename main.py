from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os
import tarfile
from azure.storage.blob import BlobServiceClient

# --- 0. تعريف المتغيرات ---
MODEL_PATH = "/app/model"
pipeline_instance = None


# --- 1. دالة لتنزيل وفك ضغط الموديل ---
def setup_model():
    global pipeline_instance

    # إذا كان الموديل موجودًا بالفعل، قم بتحميله مباشرة
    if os.path.exists(MODEL_PATH) and os.listdir(MODEL_PATH):
        print("--- Model already exists. Loading pipeline... ---")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            pipeline_instance = pipeline(
                "sentiment-analysis", model=model, tokenizer=tokenizer
            )
            print("--- Model Loaded Successfully! ---")
            return
        except Exception as e:
            print(f"Error loading existing model: {e}. Will try to re-download.")

    # إذا لم يكن الموديل موجودًا، قم بتنزيله
    print("--- Model not found. Starting download and extraction... ---")
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connect_str:
        print(
            "FATAL ERROR: AZURE_STORAGE_CONNECTION_STRING environment variable not set."
        )
        return

    CONTAINER_NAME = "models"
    MODEL_TAR_BLOB_NAME = "sentiment_model_v1.tar.gz"  # تأكدي أن هذا هو الاسم الصحيح!
    DOWNLOAD_PATH = os.path.join("/tmp", MODEL_TAR_BLOB_NAME)

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=MODEL_TAR_BLOB_NAME
        )

        print(f"Downloading {MODEL_TAR_BLOB_NAME} to {DOWNLOAD_PATH}...")
        with open(DOWNLOAD_PATH, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print("Download complete.")

        print(f"Extracting {DOWNLOAD_PATH} to {MODEL_PATH}...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        with tarfile.open(DOWNLOAD_PATH, "r:gz") as tar:
            tar.extractall(path=MODEL_PATH)
        print("Extraction complete.")

        os.remove(DOWNLOAD_PATH)
        print(f"Removed temporary file {DOWNLOAD_PATH}.")

        # بعد التنزيل، قم بتحميل الموديل
        print("--- Loading pipeline after download... ---")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        pipeline_instance = pipeline(
            "sentiment-analysis", model=model, tokenizer=tokenizer
        )
        print("--- Model Loaded Successfully! ---")

    except Exception as e:
        print(f"An error occurred during model setup: {e}")


# --- 2. تعريف نماذج البيانات ---
class PredictionRequest(BaseModel):
    texts: List[str]


class PredictionResponse(BaseModel):
    label: str
    score: float


# --- 3. إنشاء تطبيق FastAPI ---
app = FastAPI()


# --- 4. تشغيل دالة الإعداد عند بدء تشغيل التطبيق ---
@app.on_event("startup")
def startup_event():
    setup_model()


# --- 5. تعريف نقاط النهاية ---
@app.post("/predict", response_model=List[PredictionResponse])
def predict(request: PredictionRequest):
    if not pipeline_instance:
        raise HTTPException(
            status_code=503, detail="Model is not loaded or failed to load. Check logs."
        )
    if not request.texts:
        return []
    try:
        predictions = pipeline_instance(request.texts)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    if not pipeline_instance:
        return {"message": "Sentiment Analysis API is starting up, model is loading..."}
    return {"message": "Sentiment Analysis API is running."}
