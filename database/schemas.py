from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str


class NoteCreate(BaseModel):
    title: str = Field(..., max_length=256)
    body: str = Field(..., max_length=65536)


class NoteInDBForUser(NoteCreate):
    uuid: str
    created_at: datetime

  
class NoteInDB(NoteInDBForUser):  
    author: str
    is_active: bool


class StatusResponse(BaseModel):
    status_code: int
    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RoleUpdateRequest(BaseModel):
    user_email: str
    new_role: str # Admin, User
