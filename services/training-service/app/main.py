import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import mlflow
from prometheus_fastapi_instrumentator import Instrumentator
from app.db_utils import DatabaseConnection
from app.train_utils import ModelTrainer

app = FastAPI()
instrumentator = Instrumentator().instrument(app).expose(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingRequest(BaseModel):
    store: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    params: Optional[Dict] = None

@app.post("/train")
async def train_model(request: TrainingRequest):
    db = DatabaseConnection()
    db.connect()
    
    trainer = ModelTrainer()
    df = db.get_sales_data(request.store, request.start_date, request.end_date)

    if df.empty:
        raise HTTPException(status_code=400, detail="No data available for training")

    run_id, metrics, model = trainer.run_experiment(df, request.params)

    return {
        "status": "success",
        "run_id": run_id,
        "metrics": metrics
    }

@app.get("/models/{run_id}")
async def get_model_info(run_id: str):
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    return {
        "status": "success",
        "metrics": run.data.metrics,
        "parameters": run.data.params
    }
