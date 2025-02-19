from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from database.schemas import User, StatusResponse, Token
from database.mongo import get_mongo_db
from app.crud.users import UserDAO, authenticate_user, create_access_token
from app.crud.exceptions import UserAlreadeCreatedException, UserNotFoundException
from app.utils.handle_common_exceptions import handle_common_exceptions


user_routers = APIRouter()


@user_routers.post('/sign-up', response_model=StatusResponse)
@handle_common_exceptions
def create_user(body: User):
    try:
        UserDAO(mongo=get_mongo_db()).create_new_user(
            email=body.email, 
            password=body.password)

        return StatusResponse(status_code=status.HTTP_201_CREATED, detail="User registered successfully")
    except UserAlreadeCreatedException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")


@user_routers.post('/token', response_model=Token)
@handle_common_exceptions
def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends()):
    try:
        user = authenticate_user(get_mongo_db(), form_data.username, form_data.password)
        access_token = create_access_token(
            data={'sub': user.username}
        )
        return {'access_token': access_token, 'token_type': 'bearer'}
    except UserNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
