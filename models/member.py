# models/member.py
from bson import ObjectId

class Member:
    def __init__(self, mongo):
        self.db = mongo.db

    def create_member(self, name, email):
        member = {
            "name": name,
            "email": email,
            "borrowed_books": []
        }
        return self.db.members.insert_one(member)

    def get_members(self):
        return list(self.db.members.find())
