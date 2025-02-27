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
from flask import Flask, request, jsonify

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

<<<<<<< Updated upstream
# Routes pour servir le front-end (pour les pages statiques)
=======
@app.route("/test-db")
def test_db():
    try:
        # Test de la connexion à MongoDB
        collections = mongo.db.list_collection_names()
        return {"message": "Connexion MongoDB réussie", "collections": collections}, 200
    except Exception as e:
        return {"error": str(e)}, 500


    book = {
        "title": "Le Seigneur des Anneaux",
        "author": "J.R.R. Tolkien",
        "year": 1954
    }

    # Insérer le livre dans la collection 'books'
    result = mongo.db.books.insert_one(book)
    
    if result.inserted_id:
        return {"message": "Livre ajouté avec succès !", "book_id": str(result.inserted_id)}, 200
    else:
        return {"message": "Erreur lors de l'ajout du livre."}, 500
    
    
@app.route("/get-etudiant/<identifiant>", methods=["GET"])
def get_etudiant(identifiant):
    try:
        # Chercher l'étudiant dans la base de données en fonction de l'identifiant
        etudiant = mongo.db.etudiants.find_one({"identifiant": identifiant})
        
        if etudiant:
            # Convertir l'ID MongoDB en chaîne de caractères
            etudiant["_id"] = str(etudiant["_id"])
            return jsonify(etudiant), 200
        else:
            return jsonify({"message": "Étudiant non trouvé"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifiant = data.get("identifiant")
    mot_de_passe = data.get("mot_de_passe")
    
    # Logique de validation de l'identifiant et du mot de passe
    if identifiant == "doejohn" and mot_de_passe == "12345":
        return jsonify({"message": "Connexion réussie"}), 200
    else:
        return jsonify({"message": "Identifiant ou mot de passe incorrect"}), 400



@app.route("/get-books", methods=["GET"])
def get_books():
    books_collection = mongo.db.books
    
    # Récupérer tous les livres de la collection
    books_cursor = books_collection.find()
    books_list = []
    
    for book in books_cursor:
        # Convertir l'ID en chaîne de caractères
        book["_id"] = str(book["_id"])

        # Normalisation des champs
        normalized_book = {
            "codliv": book.get("codliv", "Inconnu"),  # Utiliser "Inconnu" si codliv est manquant
            "title": book.get("titreliv", book.get("title", "Titre inconnu")),  # Titre du livre
            "author": book.get("nomaut", book.get("author", "Auteur inconnu")),  # Auteur du livre
            "year": book.get("year", "Année inconnue"),  # Année de publication
            "pages": book.get("nbrpages", "Pages inconnues")  # Nombre de pages
        }

        # Ajouter le livre normalisé à la liste
        books_list.append(normalized_book)
    
    return jsonify({"books": books_list}), 200



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



@app.route("/get-etudiants", methods=["GET"])
def get_etudiants():
    try:
        etudiants = list(mongo.db.etudiants.find({}, {
            "_id": 0,
            "idetudiant": 1,
            "identifiant": 1,
            "nometd": 1,
            "prenometd": 1,
            "filiere": 1
        }))
        
        return jsonify({"etudiants": etudiants}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # Accéder à la collection des étudiants
    etudiants_collection = mongo.db.etudiants
    
    # Récupérer tous les étudiants
    etudiants_cursor = etudiants_collection.find()
    etudiants_list = []
    
    for etudiant in etudiants_cursor:
        # Convertir l'ID MongoDB en chaîne de caractères
        etudiant["_id"] = str(etudiant["_id"])

        # Normalisation des champs si nécessaire
        normalized_etudiant = {
            "idetudiant": etudiant.get("idetudiant", "Inconnu"),
            "nometd": etudiant.get("nometd", "Nom inconnu"),
            "prenometd": etudiant.get("prenometd", "Prénom inconnu"),
            "filiere": etudiant.get("filiere", "Filière inconnue"),
        }

        # Ajouter l'étudiant normalisé à la liste
        etudiants_list.append(normalized_etudiant)
    
    # Retourner la liste d'étudiants en format JSON
    return jsonify({"etudiants": etudiants_list}), 200

@app.route("/get-students-punished", methods=["GET"])
def get_students_punished():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "punition",  # Nom exact de la collection
                    "localField": "idetudiant",  # Champ dans etudiants
                    "foreignField": "cneetd",  # Champ dans punition
                    "as": "punitions"
                }
            },
            {
                "$match": {
                    "punitions": {"$ne": []}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "idetudiant": 1,
                    "nometd": 1,
                    "prenometd": 1,
                    "filiere": 1,
                    "total_punitions": {"$size": "$punitions"},
                    "punitions": {
                        "$map": {
                            "input": "$punitions",
                            "as": "pun",
                            "in": {
                                "codpun": "$$pun.codpun",
                                "datepun": "$$pun.datepun"
                            }
                        }
                    }
                }
            }
        ]

        results = list(mongo.db.etudiants.aggregate(pipeline))
        return jsonify({"punished_students": results}), 200

    except Exception as e:
        print("Erreur MongoDB :", str(e))  # Log pour débogage
        return jsonify({"error": str(e)}), 500
    try:
        # Pipeline d'agrégation pour joindre les collections
        pipeline = [
            {
                "$lookup": {
                    "from": "punition",
                    "localField": "cne_etd",  # Champ dans etudiants
                    "foreignField": "cneetd", # Champ correspondant dans punition
                    "as": "punitions"
                }
            },
            {
                "$match": {
                    "punitions": {"$ne": []}  # Filtre les étudiants avec au moins une punition
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "idetudiant": 1,
                    "nometd": 1,
                    "prenometd": 1,
                    "filiere": 1,
                    "total_punitions": {"$size": "$punitions"},
                    "punitions": {
                        "$map": {
                            "input": "$punitions",
                            "as": "pun",
                            "in": {
                                "codpun": "$$pun.codpun",
                                "datepun": "$$pun.datepun"
                            }
                        }
                    }
                }
            }
        ]

        # Exécution de l'agrégation
        results = list(mongo.db.etudiants.aggregate(pipeline))
        
        return jsonify({"punished_students": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # Accéder aux collections
    etudiants_collection = mongo.db.etudiants
    punition_collection = mongo.db.punition

    # Récupérer les punitions
    punition_cursor = punition_collection.find()

    punished_students = []

    # Parcourir les punitions
    for punition in punition_cursor:
        # Récupérer le cneetd de l'étudiant puni
        cneetd = punition.get("cneetd")

        # Trouver l'étudiant puni
        etudiant = etudiants_collection.find_one({"cne_etd": cneetd})

        # Si l'étudiant est trouvé, ajouter les informations
        if etudiant:
            punished_students.append({
                "idetudiant": etudiant.get("idetudiant"),
                "nometd": etudiant.get("nometd"),
                "prenometd": etudiant.get("prenometd"),
                "filiere": etudiant.get("filiere"),
                "codpun": punition.get("codpun"),
            })

    # Retourner la liste des étudiants punis
    return jsonify({"punished_students": punished_students}), 200

@app.route("/get-prets", methods=["GET"])
def get_prets():
    try:
        # Pipeline simplifié pour récupérer les prêts avec informations des étudiants, administrateurs et livres
        pipeline = [
            # Jointure avec la collection 'etudiants' pour récupérer les informations sur l'étudiant
            {
                "$lookup": {
                    "from": "etudiants",
                    "localField": "idetudiant",
                    "foreignField": "idetudiant",
                    "as": "etudiant_info"
                }
            },
            # Jointure avec la collection 'administrateurs' pour récupérer les informations sur l'administrateur
            {
                "$lookup": {
                    "from": "administrateurs",
                    "localField": "idadmin",
                    "foreignField": "idadmin",
                    "as": "admin_info"
                }
            },
            # Jointure avec la collection 'livres' pour récupérer les informations sur le livre
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            # Projeter les résultats en sélectionnant les champs souhaités
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "etudiant_nom": {"$arrayElemAt": ["$etudiant_info.nometd", 0]},
                    "etudiant_prenom": {"$arrayElemAt": ["$etudiant_info.prenometd", 0]},
                    "admin_nom": {"$arrayElemAt": ["$admin_info.nomadm", 0]},
                    "admin_prenom": {"$arrayElemAt": ["$admin_info.prenomadm", 0]},
                    "livre_titre": {"$arrayElemAt": ["$livre_info.titreliv", 0]},
                    "livre_auteur": {"$arrayElemAt": ["$livre_info.nomaut", 0]},
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]
        
        # Exécution du pipeline d'agrégation
        prets = list(mongo.db.prets.aggregate(pipeline))
        
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-administrators", methods=["GET"])
def get_administrators():
    admins_collection = mongo.db.administrateurs  # Remplacer 'administrateurs' par le nom de ta collection
    
    # Récupérer tous les administrateurs de la collection
    admins_cursor = admins_collection.find()
    admins_list = []
    
    for admin in admins_cursor:
        # Convertir l'ID en chaîne de caractères si nécessaire
        admin["_id"] = str(admin["_id"])

        # Normalisation des champs
        normalized_admin = {
            "numero_admin": admin.get("numero_admin", "Numéro inconnu"),  # Numéro de l'administrateur
            "identifiant": admin.get("identifiant", "Identifiant inconnu"),  # Identifiant de l'administrateur
            "motdepasse": admin.get("motdepasse", "Mot de passe inconnu"),  # Mot de passe de l'administrateur
            "nom": admin.get("nomadm", "Nom inconnu"),  # Nom de l'administrateur
            "prenom": admin.get("prenomadm", "Prénom inconnu")  # Prénom de l'administrateur
        }

        # Ajouter l'administrateur normalisé à la liste
        admins_list.append(normalized_admin)
    
    return jsonify({"administrators": admins_list}), 200

if __name__ == '__main__':
    app.run(debug=True)

# Routes pour servir le front-end
>>>>>>> Stashed changes
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
