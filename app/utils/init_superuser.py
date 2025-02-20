from database.mongo import get_db

def init_users_collection(mongo):
    user_data = { # password: admin
        "username": "admin@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$oNRaC0GolZKyNqY0pjRGyA$6T/KqsGGS7OHE/YZzOEzWrXooW5A50weHT4bVpwSOWQ",
        "role": "Superuser",
    }
    users_collection = mongo["users"]

    if users_collection.find_one({"username": user_data["username"]}) is None:
        users_collection.insert_one(user_data)
        print("User inserted successfully.")
    else:
        print("User already exists.")

if __name__ == "__main__":
    init_users_collection(get_db())
