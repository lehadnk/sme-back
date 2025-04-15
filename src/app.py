from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from communication.http.experiments import experiments_router
from communication.http.models import models_router
from communication.http.stocks import stocks_router
from communication.http.authentication import authentication_router
from communication.http.users import users_router
from config import origins

app = FastAPI()
app.include_router(models_router)
app.include_router(stocks_router)
app.include_router(experiments_router)
app.include_router(authentication_router)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
