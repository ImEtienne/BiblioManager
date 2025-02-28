from flask import Blueprint, render_template, abort, current_app
from flask_login import login_required, current_user

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
