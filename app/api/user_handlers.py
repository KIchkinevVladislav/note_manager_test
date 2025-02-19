from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from database.schemas import User, UserInDB, StatusResponse
from database.mongo import get_mongo_db
from app.crud.users import UserDAO
from app.crud.exceptions import UserAlreadeCreatedException


user_routers = APIRouter()


@user_routers.post('/sign-up', response_model=StatusResponse)
def create_user(body: User):
    try:
        UserDAO(mongo=get_mongo_db()).create_new_user(
            email=body.email, 
            password=body.password)

        return StatusResponse(status_code=201, detail="User registered successfully")
    except UserAlreadeCreatedException:
        raise HTTPException(status_code=400, detail="Username already registered")
    except Exception:
        raise HTTPException(status_code=505, detail=f"Server error. Try again later")

