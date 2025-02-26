# app.py
from flask import Flask, send_from_directory
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
from models.book import Book
from models.member import Member
from models.loan import Loan
from routes.book_routes import book_routes
from routes.member_routes import member_routes
from routes.loan_routes import loan_routes
from config import Config

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config.from_object(Config)

# Initialiser la connexion à MongoDB
mongo = PyMongo(app)

# Initialiser les modèles avec l'instance mongo
book_model = Book(mongo)
member_model = Member(mongo)
loan_model = Loan(mongo)

# Stocker les modèles dans la configuration de l'application pour les utiliser dans les blueprints
app.config['book_model'] = book_model
app.config['member_model'] = member_model
app.config['loan_model'] = loan_model

# Enregistrer les blueprints
app.register_blueprint(book_routes)
app.register_blueprint(member_routes)
app.register_blueprint(loan_routes)

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

# Routes pour servir le front-end
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

if __name__ == '__main__':
    app.run(debug=True)
