from flask import Blueprint, request, jsonify
from models.member import Member

member_routes = Blueprint('member_routes', __name__)

# Initialisation du modèle Member
member_model = Member()

# Route pour ajouter un membre
@member_routes.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if name and email:
        member_model.create_member(name, email)
        return jsonify({"message": "Membre ajouté avec succès!"}), 201
    return jsonify({"message": "Données manquantes!"}), 400

# Route pour récupérer tous les membres
@member_routes.route('/members', methods=['GET'])
def get_members():
    members = member_model.get_members()
    return jsonify(members), 200
