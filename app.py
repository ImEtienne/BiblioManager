# app.py
from flask import Flask, send_from_directory, render_template  
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import LoginManager, login_required, current_user  
from models.book import Book
from models.member import Member
from models.loan import Loan
from models.user import User  
from routes.member_routes import member_routes
from routes.loan_routes import loan_routes
from routes.auth_routes import auth_routes  
from config import Config
from flask import Flask, request, jsonify
from flask import Flask, jsonify
from routes.admin_routes import admin_routes
from routes.dashboard_routes import dashboard_routes
from routes.utilisateur_routes import utilisateur_routes
from routes.emprunts_routes import emprunts_routes
from routes.punitions_routes import punitions_routes

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config.from_object(Config)
app.config['SECRET_KEY'] = '954c77f936ae94ecc6962df467ff72d8'  

# Initialiser la connexion à MongoDB
mongo = PyMongo(app)
app.config['mongo'] = mongo  

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
login_manager.login_view = "auth_routes.login"  
login_manager.init_app(app)  

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(mongo, user_id)  

# Enregistrer les blueprints
app.register_blueprint(member_routes)
app.register_blueprint(loan_routes)
app.register_blueprint(auth_routes)  
app.register_blueprint(admin_routes)
app.register_blueprint(dashboard_routes)
app.register_blueprint(utilisateur_routes)
app.register_blueprint(emprunts_routes)
app.register_blueprint(punitions_routes)

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
