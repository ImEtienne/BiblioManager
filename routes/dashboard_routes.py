from flask import Blueprint, render_template, abort, current_app
from flask_login import login_required, current_user

dashboard_routes = Blueprint('dashboard_routes', __name__, url_prefix='/dashboard')

@dashboard_routes.route('/')  # La route devient donc "/dashboard/"
@login_required
def dashboard():
    # Exemple de récupération de statistiques (à adapter selon votre modèle)
    mongo = current_app.config['mongo']
    stats = {
        'total_books': mongo.db.books.count_documents({}),
        'total_members': mongo.db.utilisateurs.count_documents({}),
        'active_loans': mongo.db.loans.count_documents({"date_returned": None})
    }
    users = list(mongo.db.utilisateurs.find())

    # Vous pouvez aussi ajouter d'autres stats ou données de graphiques
    return render_template('dashboard.html', stats=stats, users=users)
