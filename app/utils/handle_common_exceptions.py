from functools import wraps
from fastapi import HTTPException, status
from app.crud.exceptions import CreredentialsException, UserRoleDoesNotExist, ExistRoleException

def handle_common_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (HTTPException, CreredentialsException, UserRoleDoesNotExist, ExistRoleException):
            raise
        except Exception as e:
            print(f'{e = }')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error. Try again later"
            )
    return wrapper
