from flask import Blueprint, render_template, abort, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta

dashboard_routes = Blueprint('dashboard_routes', __name__, url_prefix='/dashboard')

@dashboard_routes.route('/')  # La route devient donc "/dashboard/"
@login_required
def dashboard():
    # Exemple de récupération de statistiques (à adapter selon votre modèle)
    mongo = current_app.config['mongo']
    stats = {
        'total_books': mongo.db.books.count_documents({}),
        'total_members': mongo.db.utilisateurs.count_documents({}),
        'active_loans': mongo.db.prets.count_documents({"date_returned": None}),
        'overdue_loans': len(get_overdue_loans(mongo))
    }

    users = list(mongo.db.utilisateurs.find())
    books = list(mongo.db.books.find())  

    # Vous pouvez aussi ajouter d'autres stats ou données de graphiques
    return render_template('dashboard.html', stats=stats, users=users, books=books)

@dashboard_routes.route('/books')
@login_required
def dashboard_books():
    mongo = current_app.config['mongo']
    # Récupération des livres depuis la collection (ajustez le nom de la collection selon votre configuration)
    books = list(mongo.db.books.find())
    return render_template('dashboard_books.html', books=books)

def get_overdue_loans(mongo):
    overdue_date = datetime.utcnow() - timedelta(days=14)  # Exemple de délai de 14 jours
    overdue_loans = mongo.db.loans.find({
        "due_date": {"$lt": datetime.utcnow()},
        "date_returned": None
    })
    return list(overdue_loans)
