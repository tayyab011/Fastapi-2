from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from jose import jwt
from datetime import timedelta, datetime, timezone

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "DHSFKlihueqwdnjJJHUISDFGHWAFEYHjshffwjlweiqwpwieupcnerwiucbn"
ALGORITHM = "HS256"

OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth")


class createUsers(BaseModel):
    username: str
    email: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_user(new_user: createUsers, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.username == new_user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_model = Users(
        username=new_user.username,
        email=new_user.email,
        hashed_password=bcrypt_context.hash(new_user.password)
    )

    db.add(user_model)
    db.commit()

    return JSONResponse(
        status_code=201,
        content={"message": "User registered successfully"}
    )


def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()

    if user is None:
        return False

    if bcrypt_context.verify(password, user.hashed_password):
        return user

    return False


def create_access_token(username: str, user_id: int, express_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expire = datetime.now(timezone.utc) + express_delta
    encode.update({"exp": expire})

    return jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(OAuth2_bearer),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Token")

        user = db.query(Users).filter(
            Users.username == username
        ).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "username": username,
            "id": user_id
        }

    except HTTPException:
        raise

    except:
        raise HTTPException(status_code=401, detail="Invalid Token")


@router.post("/login")
def login_user(
    db: Session = Depends(get_db),
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()] = None,
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Fail Authentication"
        )

    token = create_access_token(
        user.username,
        user.id,
        timedelta(minutes=30)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "Login successful"
    }
