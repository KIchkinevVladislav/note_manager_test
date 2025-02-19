from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pymongo.database import Database, Collection
from jose import JWTError, jwt

from database.schemas import UserInDB
from app.crud.exceptions import UserAlreadeCreatedException, UserNotFoundException
from conf.app_conf import access_token_config


PWD_CONTEXT = CryptContext(schemes=['argon2'], deprecated='auto')
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='/user/token')


class UserDAO():
    def __init__(self, mongo: Database):
        self._mongo = mongo
    
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
