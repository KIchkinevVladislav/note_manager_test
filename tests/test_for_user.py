import re
import unittest
from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from pymongo.collection import Collection
from starlette import status

from app.crud.exceptions import UserAlreadeCreatedException
from app.crud.users import PWD_CONTEXT, UserDAO
from database.schemas import UserInDB
from main import app


class TestUserDAO(unittest.TestCase):
    def setUp(self):
        self.mock_mongo = MagicMock()
        self.mock_collection = MagicMock(spec=Collection)
        self.mock_mongo.users = self.mock_collection

        self.user_dao = UserDAO(mongo=self.mock_mongo)

    def test_get_user_found(self):
        test_user_data = {
            "username": "user@example.com",
            "hashed_password": "hashed_password",
            "role": "User",
        }
        self.mock_collection.find_one.return_value = test_user_data

        result = self.user_dao.get_user("user@example.com")

        self.assertIsInstance(result, UserInDB)
        self.assertEqual(result.username, "user@example.com")
        self.assertEqual(result.hashed_password, "hashed_password")
        self.assertEqual(result.role, "User")

        self.mock_collection.find_one.assert_called_once_with({"username": "user@example.com"})

    def test_get_user_not_found(self):
        self.mock_collection.find_one.return_value = None

        result = self.user_dao.get_user("user@example.com")

        self.assertIsNone(result)
        self.mock_collection.find_one.assert_called_once_with({"username": "user@example.com"})

    def test_create_new_user_success(self):
        self.mock_collection.find_one.return_value = None
        self.mock_collection.insert_one.return_value = None

        self.user_dao.create_new_user(email="user@example.com", password="password")

        self.mock_collection.insert_one.assert_called_once()

    def test_create_new_user_already_exists(self):
        test_user_data = {
            "username": "user@example.com",
            "hashed_password": "hashed_password",
            "role": "User",
        }
        self.mock_collection.find_one.return_value = test_user_data

        with self.assertRaises(UserAlreadeCreatedException):
            self.user_dao.create_new_user(email="user@example.com", password="password")

        self.mock_collection.insert_one.assert_not_called()

    def test_get_password_hash(self):
        hashed_password = self.user_dao._get_password_hash("password")

        self.assertTrue(PWD_CONTEXT.verify("password", hashed_password))


class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    from app.crud.users import UserDAO

    @patch.object(UserDAO, "create_new_user")
    def test_sign_up_success(self, mock_create_new_user):
        mock_create_new_user.return_value = None

        data = {
            "email": "user@example.com",
            "password": "password",
        }
        response = self.client.post("/users/sign-up", json=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            "status_code": status.HTTP_201_CREATED,
            "detail": "User registered successfully"
        })

        mock_create_new_user.assert_called_once_with(
            email="user@example.com",
            password="password"
        )

    @patch.object(UserDAO, "create_new_user")
    def test_sign_up_user_already_exists(self, mock_create_new_user):
        mock_create_new_user.side_effect = UserAlreadeCreatedException()

        data = {
            "email": "user@example.com",
            "password": "password",
        }

        response = self.client.post("/users/sign-up", json=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.json(), {"detail": "Username already registered"})

        mock_create_new_user.assert_called_once_with(
            email="user@example.com",
            password="password"
        )

    @patch("app.crud.users.UserDAO.get_user") 
    def test_login_success(self, mock_get_user):
        mock_user = UserInDB(
            username="user@example.com",
            hashed_password=PWD_CONTEXT.hash("password"),
            role="user"
        )
        mock_get_user.return_value = mock_user

        data = {
            "username": "user@example.com",
            "password": "password",
        }

        response = self.client.post("/users/token", data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(re.match(r"^[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+$", response.json()["access_token"]))
        self.assertEqual(response.json()["token_type"], "bearer")

    @patch("app.crud.users.UserDAO.get_user")
    def test_login_user_not_found(self, mock_get_user):

        mock_get_user.return_value = None

        data = {
            "username": "user@example.com",
            "password": "password",
        }

        response = self.client.post("/users/token", data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {'detail': 'Incorrect username or password'})
