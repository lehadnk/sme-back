from enum import Enum

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

from config import PostgresModel

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    researcher = "researcher"

class ModelType(str, Enum):
    gradient_boosting = "gradient_boosting"
    random_forest = "random_forest"
    xgboost = "xgboost"

class User(PostgresModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Model(PostgresModel):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    train_data_from = Column(DateTime, nullable=False)
    train_data_to = Column(DateTime, nullable=False)
    ticker = Column(String, nullable=False)
    rmse = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    regression_model = Column(String, nullable=False)
    model_filename = Column(String, nullable=False)

class Experiment(PostgresModel):
    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    train_data_from = Column(DateTime, nullable=False)
    train_data_to = Column(DateTime, nullable=False)
    test_data_from = Column(DateTime, nullable=False)
    test_data_to = Column(DateTime, nullable=False)
    ticker = Column(String, nullable=False)
    rmse = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    regression_model = Column(String, nullable=False)
    model_filename = Column(String, nullable=False)

    def __repr__(self):
        return f"<Experiment(id={self.id}, ticker={self.ticker}, rmse={self.rmse}, model_filename={self.model_filename})>"