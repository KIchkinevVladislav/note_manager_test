import logging
from functools import wraps
from typing import Callable


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='app.user_actions_log',
    filemode='a'
)

logger = logging.getLogger(__name__)


def log_user_activity(log_note_uuid: bool = False, log_username: bool = False):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user', None)
            note_uuid = kwargs.get('note_uuid', None)
            username = kwargs.get('username', None)

            logger.info(f"User - {current_user.username} used - {func.__name__} - with role: {current_user.role}")
            if log_note_uuid and note_uuid:
                logger.info(f"Note UUID: {note_uuid}")
            if log_username and username:
                logger.info(f"Get note username: {username}")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"User - {current_user.username} - with role: {current_user.role} - encountered an error in {func.__name__}: {str(e)}", exc_info=True)
                raise 
            else:
                return result
        return wrapper
    return decorator
