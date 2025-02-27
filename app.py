# app.py
from flask import Flask, send_from_directory, render_template  # MODIFICATION: Ajout de render_template pour les templates HTML d'authentification
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import LoginManager, login_required, current_user  # MODIFICATION: Importation de Flask-Login pour la gestion des sessions et de l'authentification
from models.book import Book
from models.member import Member
from models.loan import Loan
from models.user import User  # MODIFICATION: Importation du modèle User pour l'authentification
from routes.book_routes import book_routes
from routes.member_routes import member_routes
from routes.loan_routes import loan_routes
from routes.auth_routes import auth_routes  # MODIFICATION: Importation du blueprint d'authentification (login/logout)
from config import Config

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config.from_object(Config)
app.config['SECRET_KEY'] = '954c77f936ae94ecc6962df467ff72d8'  # MODIFICATION: Ajout de la clé secrète pour sécuriser les sessions

# Initialiser la connexion à MongoDB
mongo = PyMongo(app)
app.config['mongo'] = mongo  # MODIFICATION: Stocker l'instance Mongo dans la config pour l'accès dans les blueprints

# Initialiser les modèles avec l'instance mongo
book_model = Book(mongo)
member_model = Member(mongo)
loan_model = Loan(mongo)

# Stocker les modèles dans la configuration de l'application
app.config['book_model'] = book_model
app.config['member_model'] = member_model
app.config['loan_model'] = loan_model

# Initialiser Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth_routes.login"  # MODIFICATION: Définir la vue de login pour rediriger les utilisateurs non authentifiés
login_manager.init_app(app)  # MODIFICATION: Initialiser Flask-Login avec l'application

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(mongo, user_id)  # MODIFICATION: Fonction de chargement de l'utilisateur pour Flask-Login

# Enregistrer les blueprints
app.register_blueprint(book_routes)
app.register_blueprint(member_routes)
app.register_blueprint(loan_routes)
app.register_blueprint(auth_routes)  # MODIFICATION: Enregistrement du blueprint d'authentification

# Exemple d'une route protégée accessible uniquement après authentification
@app.route('/dashboard')
@login_required  # MODIFICATION: Route protégée, accessible uniquement aux utilisateurs connectés
def dashboard():
    return f"<h1>Bienvenue {current_user.username} sur votre Dashboard !</h1>"  # MODIFICATION: Affichage du dashboard avec le nom de l'utilisateur connecté

# Fonction de rappel pour les prêts en retard
def send_due_loan_reminders():
    due_loans = loan_model.get_due_loans()
    for loan in due_loans:
        loan_model.send_reminder(loan['_id'])
        print(f"Rappel envoyé pour l'emprunt {loan['_id']}.")

# Planifier l'envoi des rappels tous les jours à minuit
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_due_loan_reminders, trigger="cron", hour=0, minute=0)
scheduler.start()

# Routes pour servir le front-end (pour les pages statiques)
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

if __name__ == '__main__':
    app.run(debug=True)
