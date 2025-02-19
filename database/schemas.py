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


class Token(BaseModel):
    access_token: str
    token_type: str


class RoleUpdateRequest(BaseModel):
    user_email: str
    new_role: str # Admin, User
