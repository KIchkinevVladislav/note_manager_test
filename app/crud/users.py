from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pymongo.database import Database, Collection
from jose import JWTError, jwt

from database.schemas import UserInDB
from database.mongo import get_db
from app.crud.exceptions import UserAlreadeCreatedException, UserNotFoundException, CreredentialsException, UserRoleDoesNotExist, ExistRoleException
from conf.app_conf import access_token_config


PWD_CONTEXT = CryptContext(schemes=['argon2'], deprecated='auto')


class UserDAO():
    def __init__(self, mongo: Database):
        self._mongo = mongo
        self.user_roles = ("User", "Admin")
    
    @property
    def _collection(self) -> Collection:
        return self._mongo.users

    def get_user(self, email: str) -> UserInDB | None: 
        user_data = self._collection.find_one({"username": email})
        if user_data:
            return UserInDB(**user_data)
          
    def _get_password_hash(self, password) -> str:
        return PWD_CONTEXT.hash(password)

    def create_new_user(self, email: str, password: str, role: str="User"):
        if self.get_user(email):
            raise UserAlreadeCreatedException
        hashed_password = self._get_password_hash(password)
        user = UserInDB(username=email, hashed_password=hashed_password, role=role)

        self._collection.insert_one(user.model_dump())

    def update_user_role_in_db(self, email: str, new_role: str):
        if new_role not in self.user_roles:
            raise UserRoleDoesNotExist
        
        user = self.get_user(email=email)
        if not user:
            raise UserNotFoundException
        
        if user.role == new_role:
            raise ExistRoleException
        
        self._collection.update_one(
            {"username": email},
            {"$set": {"role": new_role}})


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)
    

def authenticate_user(mongo: Database, email: str, password: str
    ) -> UserInDB | None:
    user = UserDAO(mongo=mongo).get_user(email=email)

    if user is not None and verify_password(password, user.hashed_password):
        return user
    raise UserNotFoundException


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(
            minutes=int(access_token_config.access_token_expire_minutes)
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, access_token_config.secret_key, 
        algorithm=access_token_config.algorithm
    )
    return encoded_jwt


OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='/users/token')


def get_current_user_from_token(token: str = Depends(OAUTH2_SCHEME), db=Depends(get_db)) -> UserInDB:
    try:
        payload = jwt.decode(
            token,
            access_token_config.secret_key,
            algorithms=[access_token_config.algorithm],
        )
        email: str = payload.get('sub')
        if email is None:
            raise CreredentialsException
    except JWTError:
        raise CreredentialsException
    
    user = UserDAO(mongo=db).get_user(email=email)
    if user is None:
        raise UserNotFoundException
    return user
