from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from database.schemas import UserInDB, StatusResponse, NoteCreate, NoteInDBForUser, NoteInDB
from database.mongo import get_db
from app.crud.notes import NoteDAO
from app.crud.users import get_current_user_from_token
from app.utils.handle_common_exceptions import handle_common_exceptions
from app.utils.require_role import require_role
from app.utils.log_user_activity import log_user_activity


note_routers = APIRouter()


@note_routers.post("/create", response_model=StatusResponse)
@handle_common_exceptions
@log_user_activity()
def create_note(body: NoteCreate, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    NoteDAO(mongo=db).create_new_note(
        new_note=body,
        author=current_user.username
    )

    return StatusResponse(status_code=status.HTTP_201_CREATED, detail="Note created")


@note_routers.get("/my-notes", response_model=List[NoteInDBForUser])
@handle_common_exceptions
@log_user_activity()
def get_user_notes(current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    notes = NoteDAO(mongo=db).get_notes_by_author(current_user.username)

    return notes


@note_routers.get("/{note_uuid}", response_model=NoteInDBForUser)
@handle_common_exceptions
@log_user_activity(log_note_uuid=True)
def get_note(note_uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_note_by_uuid(note_uuid=note_uuid, author=current_user.username)

    return note


@note_routers.patch("/update_note", response_model=NoteInDBForUser)
@handle_common_exceptions
@log_user_activity(log_note_uuid=True)
def update_note(note_uuid: str, title: str = None, body: str = None, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
        updated_fields = {key: value for key, value in {"title": title, "body": body}.items() if value is not None}
        
        if not updated_fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        updated_note = NoteDAO(mongo=db).update_note_by_uuid(
            uuid=note_uuid,
            updated_data=updated_fields, 
            author=current_user.username
        )

        return updated_note


@note_routers.delete("/{note_uuid}", response_model=StatusResponse)
@handle_common_exceptions
@log_user_activity(log_note_uuid=True)
def delete_note(note_uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    NoteDAO(mongo=db).delete_note_by_uuid(uuid=note_uuid, author=current_user.username)

    return StatusResponse(status_code=status.HTTP_200_OK, detail="Note deleted")


@note_routers.delete("/staff/restore_note/{note_uuid}", response_model=StatusResponse)
@handle_common_exceptions
@log_user_activity(log_note_uuid=True)
@require_role(["Admin", "Superuser"])
def restore_note(note_uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    NoteDAO(mongo=db).restore_note_by_uuid(uuid=note_uuid)

    return StatusResponse(status_code=status.HTTP_200_OK, detail="Note restored")


@note_routers.get("/staff/get_note/{note_uuid}", response_model=NoteInDB)
@handle_common_exceptions
@log_user_activity(log_note_uuid=True)
@require_role(["Admin", "Superuser"])
def get_note_for_staff(note_uuid: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_note_by_uuid_for_staff(note_uuid=note_uuid)

    return note


@note_routers.get("/staff/get_notes", response_model=List[NoteInDB])
@handle_common_exceptions
@log_user_activity()
@require_role(["Admin", "Superuser"])
def get_notes_for_staff(current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_notes_list_for_staff()

    return note


@note_routers.get("/staff/get_notes_users", response_model=List[NoteInDB])
@handle_common_exceptions
@log_user_activity(log_username=True)
@require_role(["Admin", "Superuser"])
def get_notes_user_for_staff(username: str, current_user: UserInDB = Depends(get_current_user_from_token), db=Depends(get_db)):
    note = NoteDAO(mongo=db).get_notes_list_for_staff(author=username)

    return note
