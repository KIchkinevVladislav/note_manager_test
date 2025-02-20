from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from database.schemas import UserInDB, StatusResponse, NoteCreate, NoteInDBForUser, NoteInDB
from database.mongo import get_db
from app.crud.notes import NoteDAO
from app.crud.users import get_current_user_from_token
from app.utils.handle_common_exceptions import handle_common_exceptions
from app.utils.require_role import require_role


note_routers = APIRouter()


@note_routers.post("/create", response_model=StatusResponse)
@handle_common_exceptions
def create_note(body: NoteCreate, author: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    NoteDAO(mongo=db).create_new_note(
        new_note=body,
        author=author.username
    )

    return StatusResponse(status_code=status.HTTP_201_CREATED, detail="Note created")


@note_routers.get("/my-notes", response_model=List[NoteInDBForUser])
@handle_common_exceptions
def get_user_notes(current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    notes = NoteDAO(mongo=db).get_notes_by_author(current_user.username)
    return notes


@note_routers.get("/{note_uuid}", response_model=NoteInDBForUser)
@handle_common_exceptions
def get_note(note_uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_note_by_uuid(note_uuid=note_uuid, author=current_user.username)
    return note


@note_routers.patch("/update_note", response_model=NoteInDBForUser)
@handle_common_exceptions
def update_note(uuid: str, title: str = None, body: str = None, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
        updated_fields = {key: value for key, value in {"title": title, "body": body}.items() if value is not None}
        
        if not updated_fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")  # Ошибка, если пустой запрос

        updated_note = NoteDAO(mongo=db).update_note_by_uuid(
            uuid=uuid,
            updated_data=updated_fields, 
            author=current_user.username
        )
        return updated_note


@note_routers.delete("/{uuid}", response_model=StatusResponse)
@handle_common_exceptions
def delete_note(uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    NoteDAO(mongo=db).delete_note_by_uuid(uuid=uuid, author=current_user.username)

    return StatusResponse(status_code=status.HTTP_200_OK, detail="Note deleted")








@note_routers.delete("/staff/restore_note/{uuid}", response_model=StatusResponse)
@handle_common_exceptions
@require_role(["Admin", "Superuser"])
def restore_note(uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    NoteDAO(mongo=db).restore_note_by_uuid(uuid=uuid)

    return StatusResponse(status_code=status.HTTP_200_OK, detail="Note restored")


@note_routers.get("/staff/get_note/{uuid}", response_model=NoteInDB)
@handle_common_exceptions
@require_role(["Admin", "Superuser"])
def get_note_for_staff(note_uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_note_by_uuid_for_staff(note_uuid=note_uuid)
    return note


@note_routers.get("/staff/get_notes", response_model=List[NoteInDB])
@handle_common_exceptions
@require_role(["Admin", "Superuser"])
def get_note_for_staff(current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_notes_list_for_staff()
    return note


@note_routers.get("/staff/get_notes_users", response_model=List[NoteInDB])
@handle_common_exceptions
@require_role(["Admin", "Superuser"])
def get_notes_user_for_staff(username: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_notes_list_for_staff(author=username)
    return note
