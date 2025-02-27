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
from flask import Flask, request, jsonify
from flask import Flask, jsonify

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
    # return send_from_directory('frontend', 'index.html')
    return render_template('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)
    # return render_template('templates','index.html')

@app.route("/utilisateurs", methods=["GET"])
def get_utilisateurs():
    try:
        # Accéder à la collection des utilisateurs
        utilisateurs_collection = mongo.db.utilisateurs
       
        # Récupérer tous les utilisateurs
        utilisateurs_cursor = utilisateurs_collection.find()
        utilisateurs_list = []
       
        for utilisateur in utilisateurs_cursor:
            # Convertir l'ID MongoDB en chaîne de caractères
            utilisateur["_id"] = str(utilisateur["_id"])
           
            # Normalisation des champs si nécessaire
            normalized_utilisateur = {
                "idutilisateur": utilisateur.get("idutilisateur", "Inconnu"),
                "username": utilisateur.get("username", "Nom d'utilisateur inconnu"),
                "nomutilisateur": utilisateur.get("nomutilisateur", "Nom inconnu"),
                "prenomutilisateur": utilisateur.get("prenomutilisateur", "Prénom inconnu"),
                "role": utilisateur.get("role", "Rôle inconnu"),
                "filiere": utilisateur.get("filiere", "Filière inconnue")
            }
 
            # Ajouter l'utilisateur normalisé à la liste
            utilisateurs_list.append(normalized_utilisateur)
       
        # Retourner la liste d'utilisateurs en format JSON
        return jsonify({"utilisateurs": utilisateurs_list}), 200
   
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
