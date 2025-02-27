import uuid
from datetime import datetime

from pymongo import DESCENDING, ReturnDocument
from pymongo.database import Collection, Database

from app.utils.raise_if_not_found import raise_if_not_found
from database.schemas import NoteCreate


class NoteDAO():
    def __init__(self, mongo: Database):
        self._mongo = mongo

    @property
    def _collection(self) -> Collection:
        return self._mongo.notes

    def create_new_note(self, new_note: NoteCreate, author: str):
        note_dict = new_note.model_dump()

        note_dict["author"] = author
        note_dict["uuid"] = str(uuid.uuid4())
        note_dict["created_at"] = datetime.now().replace(second=0, microsecond=0, tzinfo=None).strftime("%Y-%m-%d %H:%M")
        note_dict["is_active"] = True

        self._collection.insert_one(note_dict)

    def get_notes_by_author(self, author: str):
        notes_cursor = self._collection.find(
            {"author": author, "is_active": True},
            {"is_active": 0, "author": 0, "_id": 0}
        ).sort("created_at", DESCENDING)

        return list(notes_cursor)

    @raise_if_not_found
    def get_note_by_uuid(self, note_uuid: str, author: str):
        note = self._collection.find_one(
            {"uuid": note_uuid, "is_active": True, "author": author},
            {"is_active": 0, "author": 0, "_id": 0}
        )
        return note
      
    @raise_if_not_found
    def update_note_by_uuid(self, uuid: str, updated_data: dict, author: str) -> dict:
        note = self._collection.find_one_and_update(
            {"uuid": uuid, "author": author, "is_active": True},
            {"$set": updated_data},
            projection={"is_active": 0, "author": 0, "_id": 0},
            return_document=ReturnDocument.AFTER
        )

        return note

    @raise_if_not_found
    def delete_note_by_uuid(self, uuid: str, author: str):
        note = self._collection.find_one_and_update(
            {"uuid": uuid, "author": author, "is_active": True},
            {"$set": {"is_active": False}}
        )
        return note

    @raise_if_not_found
    def restore_note_by_uuid(self, uuid: str):
        note = self._collection.find_one_and_update(
            {"uuid": uuid, "is_active": False},
            {"$set": {"is_active": True}},
            return_document=ReturnDocument.AFTER
        )

        return note

    @raise_if_not_found
    def get_note_by_uuid_for_staff(self, note_uuid: str):
        note = self._collection.find_one(
            {"uuid": note_uuid},
            {"_id": 0}
        )

        return note

    def get_notes_list_for_staff(self, author: str = None):

        filter = {"author": author} if author is not None else {}

        notes_cursor = self._collection.find(
            filter,
            {"_id": 0}
        ).sort("created_at", DESCENDING)

        return list(notes_cursor)
