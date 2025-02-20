from fastapi import HTTPException, status


class UserAlreadeCreatedException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UserRoleDoesNotExist(Exception):
    pass


class ExistRoleException(Exception):
    pass


class NoteNotFoundException(Exception):
    pass


class CreredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
