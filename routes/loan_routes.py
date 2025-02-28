# routes/loan_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from bson import ObjectId
from flask_login import current_user
from datetime import datetime

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

@loan_routes.route('/reserve/<book_id>', methods=['POST'])
@login_required
def reserve(book_id):
    mongo = current_app.config['mongo']
    try:
        reservation = {
            "book_id": ObjectId(book_id),
            "user_id": ObjectId(current_user.id),  # Assurez-vous que current_user.id est un ObjectId ou convertissez-le
            "reservation_date": datetime.utcnow(),
            "status": "active"
        }
        mongo.db.reservations.insert_one(reservation)
        flash("Réservation effectuée avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la réservation: {e}", "danger")
    return redirect(url_for('dashboard_routes.dashboard'))


@loan_routes.route('/borrow/<book_id>', methods=['POST'])
@login_required
def borrow(book_id):
    if current_user.role not in ['etudiant', 'admin']:
        flash("Seuls les étudiants peuvent emprunter un livre.", "warning")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    mongo = current_app.config['mongo']

    # Vérifier si le livre existe
    book = mongo.db.books.find_one({"codliv": book_id})
    if not book:
        flash("Livre introuvable.", "danger")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    # Vérifier si le livre est disponible
    if not book.get("available", True):
        flash("Ce livre est actuellement indisponible.", "warning")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    # Vérifier si l'utilisateur a déjà emprunté ce livre
    existing_loan = mongo.db.prets.find_one({
        "codliv": book_id,
        "idetudiant": str(current_user.id),  # ID de l'étudiant
        "statut": "en cours"
    })
    if existing_loan:
        flash("Vous avez déjà emprunté ce livre.", "info")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    # Enregistrement de l'emprunt
    loan = {
        "numero_admin": "001",  # À adapter selon votre logique (admin qui valide)
        "idetudiant": str(current_user.id),  # Convertir l'ObjectId en string
        "codliv": book_id,  # Code du livre
        "dateaccord": datetime.utcnow(),
        "statut": "en cours"
    }
    
    try:
        # Insérer l'emprunt dans la collection `loans`
        mongo.db.prets.insert_one(loan)
        # Marquer le livre comme indisponible
        mongo.db.books.update_one({"codliv": book_id}, {"$set": {"available": False}})
        flash("Livre emprunté avec succès !", "success")
    except Exception as e:
        flash(f"Erreur lors de l'emprunt : {e}", "danger")
    
    return redirect(url_for('dashboard_routes.dashboard_books'))



