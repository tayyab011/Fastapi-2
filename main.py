from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from typing import Annotated
from router import auth, transactions

app = FastAPI()

app.include_router(auth.router)
app.include_router(transactions.router)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
