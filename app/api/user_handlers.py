from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from database.schemas import User, UserInDB, StatusResponse, Token, RoleUpdateRequest
from database.mongo import get_db
from app.crud.users import UserDAO, authenticate_user, create_access_token, get_current_user_from_token
from app.crud.exceptions import UserAlreadeCreatedException, UserNotFoundException, UserRoleDoesNotExist, ExistRoleException
from app.utils.handle_common_exceptions import handle_common_exceptions


user_routers = APIRouter()


@user_routers.post('/sign-up', response_model=StatusResponse)
@handle_common_exceptions
def create_user(body: User, db=Depends(get_db)):
    try:
        UserDAO(mongo=db).create_new_user(
            email=body.email, 
            password=body.password)

        return StatusResponse(status_code=status.HTTP_201_CREATED, detail="User registered successfully")
    except UserAlreadeCreatedException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")


@user_routers.post('/token', response_model=Token)
@handle_common_exceptions
def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends(), db=Depends(get_db)):
        try:
            user = authenticate_user(db, form_data.username, form_data.password)
            access_token = create_access_token(
                data={'sub': user.username}
            )
            return Token(access_token=access_token,
                        token_type='bearer')
        except UserNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )


@user_routers.patch("/update-role", response_model=StatusResponse)
@handle_common_exceptions
def update_user_role(role_update: RoleUpdateRequest, current_user: UserInDB = Depends(get_current_user_from_token),  db=Depends(get_db)):
    if current_user.role != "Superuser":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    try:
        UserDAO(mongo=db).update_user_role_in_db(
            email=role_update.user_email, 
            new_role=role_update.new_role)
        return StatusResponse(status_code=status.HTTP_200_OK, detail="Successfully")
    except UserNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not exist",
            )
    except UserRoleDoesNotExist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User role does not exist: User or Admin")
    except ExistRoleException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already assigned this role")
