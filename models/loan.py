# models/loan.py
from datetime import datetime, timedelta
from bson import ObjectId

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
        return self.db.loans.insert_one(loan)

    def return_book(self, loan_id):
        self.db.loans.update_one({"_id": ObjectId(loan_id)}, {"$set": {"date_returned": datetime.now()}})

    def get_due_loans(self):
        # Considère un prêt en retard s’il a été emprunté il y a plus de 14 jours et n'est pas encore retourné
        fourteen_days_ago = datetime.now() - timedelta(days=14)
        return list(self.db.loans.find({
            "date_borrowed": {"$lte": fourteen_days_ago},
            "date_returned": None
        }))

    def send_reminder(self, loan_id):
        # Ici, vous pouvez intégrer l'envoi d'un email.
        print(f"Rappel envoyé pour l'emprunt {loan_id}")
