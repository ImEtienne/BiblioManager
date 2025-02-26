# routes/member_routes.py
from flask import Blueprint, request, jsonify, current_app

member_routes = Blueprint('member_routes', __name__)

@member_routes.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"message": "Données manquantes!"}), 400

    member_model = current_app.config['member_model']
    member_model.create_member(name, email)
    return jsonify({"message": "Membre ajouté avec succès!"}), 201

@member_routes.route('/members', methods=['GET'])
def get_members():
    member_model = current_app.config['member_model']
    members = member_model.get_members()
    return jsonify(members), 200
