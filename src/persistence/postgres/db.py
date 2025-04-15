from datetime import datetime

from sqlalchemy import func

from config import SessionLocal, get_db
from persistence.postgres.models import Experiment, Model, User


def save_experiment(experiment):
    with SessionLocal() as db:
        db.add(experiment)
        db.commit()
        db.refresh(experiment)

def save_model(model):
    with SessionLocal() as db:
        db.add(model)
        db.commit()
        db.refresh(model)

def save_user(user: User):
    with SessionLocal() as db:
        db.add(user)
        db.commit()
        db.refresh(user)

def find_user_by_id(id: int):
    db = next(get_db())
    return db.query(User).filter_by(id=id).one_or_none()

def find_user_by_username(username: str):
    db = next(get_db())
    return db.query(User).filter_by(username=username).one_or_none()

def find_experiment_by_id(id: int):
    db = next(get_db())
    return db.query(Experiment).filter_by(id=id).one_or_none()

def get_best_model_for_date_and_ticker(ticker: str, date: str):
    passed_date_obj = datetime.strptime(date, '%Y-%m-%d')
    with SessionLocal() as db:
        return db.query(Model).filter(
            Model.ticker == ticker,
            Model.train_data_to >= passed_date_obj
        ).order_by(Model.rmse).first()

def get_best_models_for_tickers_with_train_data_to_at_least(date: str):
    with SessionLocal() as db:
        subquery = (
            db.query(
                Model.id,
                Model.ticker,
                Model.rmse,
                func.row_number().over(
                    partition_by=Model.ticker,
                    order_by=Model.rmse.asc()
                ).label("rn")
            )
            .filter(Model.train_data_to <= date)
            .subquery()
        )

        query = db.query(Model).filter(Model.id.in_(
            db.query(subquery.c.id).filter(subquery.c.rn == 1)
        ))

        return query.all()