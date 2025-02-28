from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

profile_routes = Blueprint('profile_routes', __name__)

@profile_routes.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Traitement du formulaire de mise à jour du profil
        username = request.form.get('username')
        nomutilisateur = request.form.get('nomutilisateur')
        prenomutilisateur = request.form.get('prenomutilisateur')
        filiere = request.form.get('filiere')
        new_password = request.form.get('password')
        
        # Vous pouvez ajouter ici la logique de mise à jour en base de données...
        mongo = current_app.config['mongo']
        update_data = {
            "username": username,
            "nomutilisateur": nomutilisateur,
            "prenomutilisateur": prenomutilisateur,
            "filiere": filiere
        }
        if new_password:
            update_data["password"] = generate_password_hash(new_password)
        
        mongo.db.utilisateur.update_one({"_id": current_user._id}, {"$set": update_data})
        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for('profile_routes.profile'))
        
    return render_template('profile.html')
