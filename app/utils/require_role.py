from functools import wraps
from typing import Callable, List

from fastapi import Depends, HTTPException, status

from app.crud.users import get_current_user_from_token
from database.schemas import UserInDB


def require_role(allowed_roles: List[str]):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, current_user: UserInDB = Depends(get_current_user_from_token), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action"
                )
            return func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
