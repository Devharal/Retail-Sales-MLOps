import os
import mlflow
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import pandas as pd
from datetime import datetime
from app.db_utils import DatabaseConnection
from app.monitoring import MonitoringMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Retail Sales Prediction API")
instrumentator = Instrumentator().instrument(app).expose(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app.middleware('http')(MonitoringMiddleware())
class PredictionRequest(BaseModel):
    store: int
    date: str
    promo: int
    stateholiday: str
    schoolholiday: int

class PredictionResponse(BaseModel):
    store: int
    date: str
    predicted_sales: float
    model_version: str

def load_model(run_id: str):
    try:
        mlflow.set_tracking_uri(f"http://mlflow:{os.getenv('MLFLOW_PORT')}")
        model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def prepare_features(request: PredictionRequest) -> pd.DataFrame:
    date = pd.to_datetime(request.date)
    features = {
        "store": request.store,
        "year": date.year,
        "month": date.month,
        "day": date.day,
        "day_of_week": date.dayofweek,
        "promo": request.promo,
        "stateholiday": {"0": 0, "a": 1, "b": 2, "c": 3}[request.stateholiday],
        "schoolholiday": request.schoolholiday
    }
    return pd.DataFrame([features])

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        mlflow.set_tracking_uri("http://mlflow:5050")
        # client = mlflow.tracking.MlflowClient()
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment("1")
        print(experiment)
        print(client)
        runs = client.search_runs(experiment_ids=["1"], order_by=["metrics.r2 DESC"])
        print(runs)
        if not runs:
            raise HTTPException(status_code=404, detail="No trained models found")
        best_run = runs[0]
        model = load_model(best_run.info.run_id)
        features = prepare_features(request)
        prediction = model.predict(features)[0]
        print(prediction)

        db = DatabaseConnection()
        db.connect()
        prediction_data = pd.DataFrame({
            "store": [request.store],
            "date": [request.date],
            "predicted_sales": [prediction],
            "prediction_timestamp": [datetime.now()]
        })
        db.save_predictions(prediction_data)

        return PredictionResponse(
            store=request.store,
            date=request.date,
            predicted_sales=float(prediction),
            model_version=best_run.info.run_id
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/model/info")
async def model_info():
    try:
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(experiment_ids=["1"], order_by=["metrics.r2 DESC"])
        if not runs:
            return {"status": "no models available"}
        best_run = runs[0]
        return {
            "status": "success",
            "model_version": best_run.info.run_id,
            "metrics": best_run.data.metrics,
            "training_timestamp": best_run.info.start_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
