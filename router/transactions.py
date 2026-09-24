from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal
from datetime import date as Date
from database import SessionLocal
from models import Transactions
from router.auth import get_current_user

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TransactionCreate(BaseModel):
    title: str
    amount: float = Field(gt=0, description="Amount must be positive")
    type: Literal["income", "expense"]
    category: str
    date: Date


class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = Field(default=None)
    category: Optional[str] = Field(default=None)
    date: Optional[Date] = Field(default=None)

@router.post("/transactions")
def create_transaction(
    user: user_dependency,
    db: Annotated[Session, Depends(get_db)],
    new_transaction: TransactionCreate
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    transaction_model = Transactions(
        **new_transaction.model_dump(),
        owner_id=user.get("id")
    )

    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    raise HTTPException(status_code=201, detail="Transaction created successfully")


@router.get("/transactions")
def read_transactions(
    user: user_dependency,
    db: Annotated[Session, Depends(get_db)]
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    ).all()


@router.get("/transactions/filter")
def filter_transactions(
    user: user_dependency,
    db: Annotated[Session, Depends(get_db)],
    type: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    minimum_amount: Optional[float] = Query(default=None, gt=0),
    maximum_amount: Optional[float] = Query(default=None, gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = db.query(Transactions).filter(
        Transactions.owner_id == user.get("id")
    )

    if type is not None:
        query = query.filter(Transactions.type == type)

    if category is not None:
        query = query.filter(Transactions.category == category)

    if minimum_amount is not None:
        query = query.filter(Transactions.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(Transactions.amount <= maximum_amount)

    return query.all()


@router.get("/transactions/{transaction_id}")
def read_specific_transaction(
    user: user_dependency,
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    specific_transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id
    ).filter(
        Transactions.owner_id == user.get("id")
    ).first()

    if not specific_transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return specific_transaction


@router.put("/transactions/{transaction_id}")
def update_transaction(
    user: user_dependency,
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)],
    update_transaction: TransactionUpdate
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id
    ).filter(
        Transactions.owner_id == user.get("id")
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    update_data = update_transaction.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    user: user_dependency,
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    transaction = db.query(Transactions).filter(
        Transactions.id == transaction_id
    ).filter(
        Transactions.owner_id == user.get("id")
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }
