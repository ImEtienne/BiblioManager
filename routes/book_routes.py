from flask import Blueprint, request, jsonify
from models.book import Book

book_routes = Blueprint('book_routes', __name__)

# Initialisation du modèle Book
book_model = Book()

# Route pour ajouter un livre
@book_routes.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')

    if title and author:
        book_model.create_book(title, author)
        return jsonify({"message": "Livre ajouté avec succès!"}), 201
    return jsonify({"message": "Données manquantes!"}), 400

# Route pour récupérer tous les livres
@book_routes.route('/books', methods=['GET'])
def get_books():
    books = book_model.get_books()
    return jsonify(books), 200
