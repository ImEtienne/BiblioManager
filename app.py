from flask import Flask, send_from_directory, jsonify
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

# Configurer l'application Flask avec MongoDB
app.config.from_object(Config)

# Initialiser la connexion à MongoDB
mongo = PyMongo(app)

# Initialiser les modèles
book_model = Book(mongo)
member_model = Member(mongo)
loan_model = Loan(mongo)

# Enregistrer les routes
app.register_blueprint(book_routes)
app.register_blueprint(member_routes)
app.register_blueprint(loan_routes)

# Fonction pour envoyer les rappels de retour
def send_due_loan_reminders():
    overdue_loans = loan_model.get_due_loans()
    for loan in overdue_loans:
        loan_model.send_reminder(loan['_id'])
        # Tu peux ici envoyer un email via un service comme SendGrid ou SMTP
        print(f"Rappel envoyé pour l'emprunt {loan['_id']}.")

# Planifier l'envoi des rappels tous les jours à minuit
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_due_loan_reminders, trigger="interval", days=1, hour=0, minute=0)
scheduler.start()

# Route pour servir la page d'accueil (le front-end)
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

# Route pour servir les fichiers statiques (CSS, JS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

if __name__ == '__main__':
    app.run(debug=True)
