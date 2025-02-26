class Book:
    def __init__(self, mongo):
        self.db = mongo.db

    def create_book(self, title, author):
        book = {
            "title": title,
            "author": author,
            "available": True
        }
        self.db.books.insert_one(book)

    def get_books(self):
        return list(self.db.books.find())
    
    def get_book_by_id(self, book_id):
        return self.db.books.find_one({"_id": book_id})
    
    def update_availability(self, book_id, available):
        self.db.books.update_one({"_id": book_id}, {"$set": {"available": available}})
