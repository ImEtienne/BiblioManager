from datetime import datetime

class Loan:
    def __init__(self, mongo):
        self.db = mongo.db

    def create_loan(self, member_id, book_id):
        loan = {
            "member_id": member_id,
            "book_id": book_id,
            "date_borrowed": datetime.now(),
            "date_returned": None
        }
        self.db.loans.insert_one(loan)

    def return_book(self, loan_id):
        self.db.loans.update_one({"_id": loan_id}, {"$set": {"date_returned": datetime.now()}})
