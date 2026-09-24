from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal
from models import Transactions
from datetime import date


def override_get_current_user():
    return {
        "id": 1,
        "username": "testuser"
    }


app.dependency_overrides[
    get_current_user
] = override_get_current_user


def test_read_transactions():
    response = client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK


def test_read_specific_transaction():
    db = SessionLocal()

    transaction = Transactions(
        title="Test Transaction",
        amount=500,
        type="expense",
        category="Food",
        date=date(2026, 9, 23),
        owner_id=1
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    transaction_id = transaction.id

    db.close()

    response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == status.HTTP_200_OK


def test_create_transaction():
    response = client.post(
        "/transactions",
        json={
            "title": "Test Expense",
            "amount": 300,
            "type": "expense",
            "category": "Food",
            "date": "2026-09-23"
        }
    )

    assert response.status_code == status.HTTP_200_OK


def test_update_transaction():
    db = SessionLocal()

    transaction = Transactions(
        title="Old Title",
        amount=500,
        type="expense",
        category="Food",
        date=date(2026, 9, 23),
        owner_id=1
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    transaction_id = transaction.id

    db.close()

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "title": "Updated Title",
            "amount": 700
        }
    )

    assert response.status_code == status.HTTP_200_OK


def test_delete_transaction():
    db = SessionLocal()

    transaction = Transactions(
        title="Delete Transaction",
        amount=400,
        type="expense",
        category="Shopping",
        date=date(2026, 9, 23),
        owner_id=1
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    transaction_id = transaction.id

    db.close()

    response = client.delete(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == status.HTTP_200_OK
