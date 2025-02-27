# models/user.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']
        self.role = user_data.get('role', 'user')  # 'admin', 'gestionnaire', 'invité', 'user'.

    @staticmethod
    def get_user_by_id(mongo, user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_user_by_username(mongo, username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create_user(mongo, username, password, role="user"):
        hashed_password = generate_password_hash(password)
        user_data = {
            "username": username,
            "password": hashed_password,
            "role": role
        }
        mongo.db.users.insert_one(user_data)
