from contextlib import contextmanager

import clickhouse_connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from queue import Queue
from threading import Lock

DATABASE_URL = "postgresql://postgres:pwd@localhost/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
PostgresModel = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ClickHouseConnectionPool:
    def __init__(self, size=5):
        self.pool = Queue(maxsize=size)
        self.lock = Lock()
        for _ in range(size):
            client = clickhouse_connect.get_client(
                host="localhost",
                port=8123,  # Use HTTP port
                username="default",
                password="qwe",
                database="default",
            )
            self.pool.put(client)

    @contextmanager
    def get_client(self):
        print("Get client: remaining =", self.pool.qsize())

        client = self.pool.get()
        try:
            yield client
        finally:
            self.pool.put(client)

    def release_client(self, client):
        self.pool.put(client)

    def close_all(self):
        while not self.pool.empty():
            client = self.pool.get()
            client.close()

pool = ClickHouseConnectionPool(size=50)

EXPERIMENT_MODELS_DIR = "/tmp"

origins = [
    "*",
]

jwt_secret = "secret"