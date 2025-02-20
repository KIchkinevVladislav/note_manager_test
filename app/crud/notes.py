from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from database.schemas import User, UserInDB, StatusResponse, Token, RoleUpdateRequest, NoteCreate
from database.mongo import get_db
from app.crud.users import UserDAO, authenticate_user, create_access_token, get_current_user_from_token
from app.crud.exceptions import UserAlreadeCreatedException, UserNotFoundException, UserRoleDoesNotExist, ExistRoleException
from app.utils.handle_common_exceptions import handle_common_exceptions


note_routers = APIRouter()


@note_routers.post('/create', response_model=StatusResponse)
@handle_common_exceptions
def create_note(body: NoteCreate, db=Depends(get_db)):
    pass
    # try:
    #     UserDAO(mongo=db).create_new_user(
    #         email=body.email, 
    #         password=body.password)

    #     return StatusResponse(status_code=status.HTTP_201_CREATED, detail="User registered successfully")
    # except UserAlreadeCreatedException:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
