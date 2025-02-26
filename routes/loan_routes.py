from flask import Blueprint, request, jsonify
from models.loan import Loan

loan_routes = Blueprint('loan_routes', __name__)

# Initialisation du modèle Loan
loan_model = Loan()

# Route pour emprunter un livre
@loan_routes.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    member_id = data.get('member_id')
    book_id = data.get('book_id')

    if member_id and book_id:
        loan_model.create_loan(member_id, book_id)
        return jsonify({"message": "Emprunt créé avec succès!"}), 201
    return jsonify({"message": "Données manquantes!"}), 400

# Route pour retourner un livre
@loan_routes.route('/loans/return', methods=['POST'])
def return_book():
    data = request.get_json()
    loan_id = data.get('loan_id')

    if loan_id:
        loan_model.return_book(loan_id)
        return jsonify({"message": "Livre retourné avec succès!"}), 200
    return jsonify({"message": "Données manquantes!"}), 400