from functools import wraps
from fastapi import HTTPException, status

def handle_common_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error. Try again later"
            )
    return wrapper
