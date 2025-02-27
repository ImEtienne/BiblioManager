from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from bson import ObjectId
from flask import current_app

utilisateur_routes = Blueprint('utilisateur_routes', __name__)



@utilisateur_routes.route('/utilisateurs')  # La route devient donc "/utilisateurs/"

@login_required
def utilisateurs():
    # Exemple de récupération de statistiques (à adapter selon votre modèle)
    mongo = current_app.config['mongo']
    
    users = list(mongo.db.utilisateurs.find())

    # Vous pouvez aussi ajouter d'autres stats ou données de graphiques
    return render_template('utilisateurs.html',  users=users)
