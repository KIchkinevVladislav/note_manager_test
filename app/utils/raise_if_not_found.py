from functools import wraps

from app.crud.exceptions import NoteNotFoundException


def raise_if_not_found(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            note = func(*args, **kwargs)
            if not note:
                raise NoteNotFoundException
            return note
        return wrapper
