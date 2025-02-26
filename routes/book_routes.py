# routes/book_routes.py
from flask import Blueprint, request, jsonify, current_app

book_routes = Blueprint('book_routes', __name__)

@book_routes.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({"message": "Données manquantes!"}), 400

    book_model = current_app.config['book_model']
    book_model.create_book(title, author)
    return jsonify({"message": "Livre ajouté avec succès!"}), 201

@book_routes.route('/books', methods=['GET'])
def get_books():
    book_model = current_app.config['book_model']
    books = book_model.get_books()
    return jsonify(books), 200
