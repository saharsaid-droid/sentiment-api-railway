from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os

MODEL_PATH = "/app/model"
pipeline_instance = None

print("--- Loading Model ---")
if os.path.exists(MODEL_PATH):
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        pipeline_instance = pipeline(
            "sentiment-analysis", model=model, tokenizer=tokenizer
        )
        print("--- Model Loaded Successfully! ---")
    except Exception as e:
        print(f"Failed to load model: {e}")
else:
    print(f"Model directory not found at {MODEL_PATH}. API will not work.")


class PredictionRequest(BaseModel):
    texts: List[str]


class PredictionResponse(BaseModel):
    label: str
    score: float


app = FastAPI()


@app.post("/predict", response_model=List[PredictionResponse])
def predict(request: PredictionRequest):
    if not pipeline_instance:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    if not request.texts:
        return []
    try:
        predictions = pipeline_instance(request.texts)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Sentiment Analysis API is running."}
