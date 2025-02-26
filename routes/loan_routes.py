# routes/loan_routes.py
from flask import Blueprint, request, jsonify, current_app

loan_routes = Blueprint('loan_routes', __name__)

@loan_routes.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    member_id = data.get('member_id')
    book_id = data.get('book_id')

    if not member_id or not book_id:
        return jsonify({"message": "Données manquantes!"}), 400

    loan_model = current_app.config['loan_model']
    loan_model.create_loan(member_id, book_id)
    return jsonify({"message": "Emprunt créé avec succès!"}), 201

@loan_routes.route('/loans/return', methods=['POST'])
def return_book():
    data = request.get_json()
    loan_id = data.get('loan_id')

    if not loan_id:
        return jsonify({"message": "Données manquantes!"}), 400

    loan_model = current_app.config['loan_model']
    loan_model.return_book(loan_id)
    return jsonify({"message": "Livre retourné avec succès!"}), 200
