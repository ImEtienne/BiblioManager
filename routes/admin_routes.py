from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from bson import ObjectId

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        abort(403)
    mongo = current_app.config['mongo']
    # Exemple de récupération des données
    users = list(mongo.db.utilisateurs.find())
    
    # Vous pouvez définir un dictionnaire de paramètres par défaut ou récupérer depuis la DB
    settings = {
        "siteName": "Bibliothèque Moderne",
        "notificationEmail": "contact@example.com"
    }
    # Logs et audit : récupérez vos logs (ici, une liste vide en exemple)
    logs = []
    return render_template('admin.html', users=users, settings=settings, logs=logs)

@admin_routes.route('/user/create', methods=['POST'])
@login_required
def create_user():
    # Seuls les admin et gestionnaire peuvent créer des utilisateurs
    if current_user.role not in ['admin', 'gestionnaire']:
        flash("Vous n'êtes pas autorisé à créer des utilisateurs.", "danger")
        return redirect(url_for('admin_routes.admin_panel'))
    
    # Récupération des données du formulaire
    username = request.form.get('username')
    email = request.form.get('email')
    nomutilisateur = request.form.get('nomutilisateur')
    prenomutilisateur = request.form.get('prenomutilisateur')
    filiere = request.form.get('filiere')
    role = request.form.get('role')
    password = request.form.get('password')
    
    if not username or not email or not password:
        flash("Les champs Username, Email et Mot de passe sont obligatoires.", "warning")
        return redirect(url_for('admin_routes.admin_panel'))
    
    # Hashage du mot de passe
    hashed_password = generate_password_hash(password)
    
    mongo = current_app.config['mongo']
    
    # Préparation du document utilisateur
    new_user = {
        "username": username,
        "email": email,
        "nomutilisateur": nomutilisateur,
        "prenomutilisateur": prenomutilisateur,
        "role": role,
        "filiere": filiere,
        "password": hashed_password
    }
    
    try:
        mongo.db.utilisateurs.insert_one(new_user)
        flash("Utilisateur créé avec succès !", "success")
    except Exception as e:
        flash(f"Erreur lors de la création de l'utilisateur : {e}", "danger")
    
    return redirect(url_for('admin_routes.admin_panel'))


@admin_routes.route('/user/delete/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # Vérifier que l'utilisateur est admin ou gestionnaire
    if current_user.role not in ['admin', 'gestionnaire']:
        flash("Vous n'êtes pas autorisé à supprimer des utilisateurs.", "danger")
        return redirect(url_for('admin_routes.admin_panel'))
    
    mongo = current_app.config['mongo']
    
    try:
        mongo.db.utilisateurs.delete_one({"_id": ObjectId(user_id)})
        flash("Utilisateur supprimé avec succès !", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression de l'utilisateur : {e}", "danger")
    
    return redirect(url_for('admin_routes.admin_panel'))
