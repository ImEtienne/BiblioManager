from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from models.loan import Loan
from flask import current_app


emprunts_routes = Blueprint('emprunts_routes', __name__)
@emprunts_routes.route('/emprunts')  
@login_required
def emprunts():
    # Exemple de récupération de statistiques (à adapter selon votre modèle)
    mongo = current_app.config['mongo']
    
    prets = list(mongo.db.prets.find())

    # Vous pouvez aussi ajouter d'autres stats ou données de graphiques
    return render_template('emprunts.html',  prets=prets)
