from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pymongo.database import Database, Collection

from database.schemas import UserInDB
from app.crud.exceptions import UserAlreadeCreatedException


PWD_CONTEXT = CryptContext(schemes=['argon2'], deprecated='auto')
# OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='/user/token')


class UserDAO():
    def __init__(self, mongo: Database):
        self._mongo = mongo
    
    @property
    def _collection(self) -> Collection:
        return self._mongo.users

    def get_user(self, email: str) -> Optional[UserInDB]: 
        user_data = self._collection.find_one({"username": email})
        if user_data:
            return UserInDB(**user_data)
          
    def _get_password_hash(self, password):
        return PWD_CONTEXT.hash(password)

    def create_new_user(self, email: str, password: str, role: str="User"):
        if self.get_user(email):
            raise UserAlreadeCreatedException
        hashed_password = self._get_password_hash(password)
        user = UserInDB(username=email, hashed_password=hashed_password, role=role)

        self._collection.insert_one(user.model_dump())

