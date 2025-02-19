from pydantic import BaseModel, EmailStr, field_validator


class User(BaseModel):
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str


class StatusResponse(BaseModel):
    status_code: int
    detail: str
