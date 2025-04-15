from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from config import get_db
from persistence.postgres.models import Model

models_router = APIRouter()

@models_router.get("/models/")
def get_models(db: Session = Depends(get_db)):
    models = db.query(Model).all()
    return {"items": models}
