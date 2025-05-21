from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from config import get_db
from persistence.postgres.db import find_experiment_by_id, find_user_by_id
from persistence.postgres.models import Experiment
from domain.regression import perform_experiment, create_model_from_experiment

experiments_router = APIRouter()

class MakeExperimentRequest(BaseModel):
    ticker: str
    train_from: str
    train_to: str
    test_from: str
    test_to: str
    model: str

class MakeExperimentResponse(BaseModel):
    id: int
    rmse: float
    min: float
    max: float
    dates: list
    y_test: list
    y_pred: list

@experiments_router.post("/experiments/make")
def make_experiment(request: MakeExperimentRequest):
    rmse, min, max, dates, y_test, y_pred, experiment = perform_experiment(
        author=find_user_by_id(1),
        ticker=request.ticker,
        train_from=request.train_from,
        train_to=request.train_to,
        test_from=request.test_from,
        test_to=request.test_to,
        model_type=request.model
    )

    return MakeExperimentResponse(
        id=experiment.id,
        rmse=rmse,
        min=min,
        max=max,
        dates=dates,
        y_test=y_test,
        y_pred=y_pred
    )

@experiments_router.post("/experiments/{id}/save")
async def save_model_from_experiment(id: int):
    experiment = find_experiment_by_id(id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Run the blocking create_model_from_experiment in a threadpool, await it
    model = await run_in_threadpool(create_model_from_experiment, experiment)

    # If `model` is not JSON serializable, convert it or return something else
    return model

@experiments_router.get("/experiments")
def list_experiements(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, le=100)
):
    offset = (page - 1) * page_size
    return db.query(Experiment).offset(offset).limit(page_size).all()