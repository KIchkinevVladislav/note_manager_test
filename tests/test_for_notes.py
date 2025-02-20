import unittest
from unittest.mock import MagicMock
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import ReturnDocument
from datetime import datetime
import uuid

from app.crud.notes import NoteDAO
from database.schemas import NoteCreate

class TestNoteDAO(unittest.TestCase):
    def setUp(self):
        self.mock_mongo = MagicMock(spec=Database)
        self.mock_collection = MagicMock(spec=Collection)
        self.mock_mongo.notes = self.mock_collection

        self.note_dao = NoteDAO(mongo=self.mock_mongo)

    def test_create_new_note(self):
        new_note = NoteCreate(title="Test Note", body="I love you, bro")
        author = "test_user"
        
        self.note_dao.create_new_note(new_note, author)
        
        self.mock_collection.insert_one.assert_called_once()
        inserted_data = self.mock_collection.insert_one.call_args[0][0]
        self.assertEqual(inserted_data["title"], "Test Note")
        self.assertEqual(inserted_data["body"], "I love you, bro")
        self.assertEqual(inserted_data["author"], "test_user")
        self.assertIn("uuid", inserted_data)
        self.assertIn("created_at", inserted_data)
        self.assertTrue(inserted_data["is_active"])

    def test_get_notes_by_author(self):
        test_notes = [
            {"title": "Note 1", "body": "Buy spam", "created_at": "2024-02-20 12:00"},
            {"title": "Note 2", "body": "Buy spam and baikal", "created_at": "2024-02-19 10:00"},
        ]
        self.mock_collection.find.return_value.sort.return_value = test_notes

        result = self.note_dao.get_notes_by_author("test_user")

        self.assertEqual(result, test_notes)
        self.mock_collection.find.assert_called_once_with(
            {"author": "test_user", "is_active": True},
            {"is_active": 0, "author": 0, "_id": 0}
        )

    def test_get_note_by_uuid(self):
        test_note = {"title": "Test Note", "content": "Buy spam"}
        self.mock_collection.find_one.return_value = test_note

        result = self.note_dao.get_note_by_uuid("test-uuid", "test_user")
        
        self.assertEqual(result, test_note)
        self.mock_collection.find_one.assert_called_once_with(
            {"uuid": "test-uuid", "is_active": True, "author": "test_user"},
            {"is_active": 0, "author": 0, "_id": 0}
        )

    def test_update_note_by_uuid(self):
        updated_data = {"title": "Updated Title"}
        updated_note = {"title": "Updated Title", "content": "Buy spam"}
        self.mock_collection.find_one_and_update.return_value = updated_note

        result = self.note_dao.update_note_by_uuid("test-uuid", updated_data, "test_user")
        
        self.assertEqual(result, updated_note)
        self.mock_collection.find_one_and_update.assert_called_once_with(
            {"uuid": "test-uuid", "author": "test_user", "is_active": True},
            {"$set": updated_data},
            projection={'is_active': 0, 'author': 0, '_id': 0},
            return_document=ReturnDocument.AFTER
        )

    def test_delete_note_by_uuid(self):
        self.mock_collection.find_one_and_update.return_value = {"title": "Deleted Note"}
        
        result = self.note_dao.delete_note_by_uuid("test-uuid", "test_user")
        
        self.assertEqual(result, {"title": "Deleted Note"})
        self.mock_collection.find_one_and_update.assert_called_once_with(
            {"uuid": "test-uuid", "author": "test_user", "is_active": True},
            {"$set": {"is_active": False}}
        )

    def test_restore_note_by_uuid(self):
        restored_note = {"title": "Restored Note", "is_active": True}
        self.mock_collection.find_one_and_update.return_value = restored_note

        result = self.note_dao.restore_note_by_uuid("test-uuid")
        
        self.assertEqual(result, restored_note)
        self.mock_collection.find_one_and_update.assert_called_once_with(
            {"uuid": "test-uuid", "is_active": False},
            {"$set": {"is_active": True}},
            return_document=ReturnDocument.AFTER
        )

    def test_get_note_by_uuid_for_staff(self):
        test_note = {"title": "Staff Note", "content": "Confidential"}
        self.mock_collection.find_one.return_value = test_note

        result = self.note_dao.get_note_by_uuid_for_staff("test-uuid")
        
        self.assertEqual(result, test_note)
        self.mock_collection.find_one.assert_called_once_with(
            {"uuid": "test-uuid"},
            {"_id": 0}
        )

    def test_get_notes_list_for_staff(self):
        test_notes = [
            {"title": "Note 1", "body": "Buy spam"},
            {"title": "Note 2", "body": "Buy spam and cola"},
        ]
        self.mock_collection.find.return_value.sort.return_value = test_notes

        result = self.note_dao.get_notes_list_for_staff()
        
        self.assertEqual(result, test_notes)
        self.mock_collection.find.assert_called_once_with({}, {"_id": 0})
