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
from config_settings import Config
from flask import Flask, jsonify



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


@app.route("/get-etudiants", methods=["GET"])
def get_etudiants():
    try:
        etudiants = list(mongo.db.etudiants.find({}, {
            "_id": 0,
            "idetudiant": 1,
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
        pipeline = [
            # Étape 1: Jointure avec étudiants (sans unwind)
            {
                "$lookup": {
                    "from": "etudiants",
                    "localField": "idetudiant",
                    "foreignField": "cne_ididetudiant",
                    "as": "etudiant_info"
                }
            },
            # Étape 2: Jointure avec administrateurs (sans unwind)
            {
                "$lookup": {
                    "from": "administrateurs",
                    "localField": "idadmin",
                    "foreignField": "cinadm",
                    "as": "admin_info"
                }
            },
            # Étape 3: Jointure avec livres (sans unwind)
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            # Étape 4: Récupération du premier élément des arrays
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "etudiant": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$etudiant_info", 0]},
                            {"erreur": "Étudiant introuvable"}
                        ]
                    },
                    "admin": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$admin_info", 0]},
                            {"erreur": "Admin introuvable"}
                        ]
                    },
                    "livre": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$livre_info", 0]},
                            {"erreur": "Livre introuvable"}
                        ]
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            },
            # Étape 5: Formatage final
            {
                "$project": {
                    "pret_id": 1,
                    "etudiant.nom": "$etudiant.nometd",
                    "etudiant.prenom": "$etudiant.prenometd",
                    "admin.nom": "$admin.nomadm",
                    "admin.prenom": "$admin.prenomadm",
                    "livre.titre": "$livre.titreliv",
                    "livre.auteur": "$livre.nomaut",
                    "date_emprunt": 1,
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


    try:
        pipeline = [
            # Conversion des IDs en string pour compatibilité
            {
                "$addFields": {
                    "idetudiant_str": {"$toString": "$idetudiant"},
                    "codeliv_str": {"$toString": "$codeliv"},
                    "idadmin_str": {"$toString": "$idadmin"}
                }
            },
            
            # Jointure avec étudiants
            {
                "$lookup": {
                    "from": "etudiants",
                    "localField": "idetudiant_str",
                    "foreignField": "cne_etd",  # Vérifier le nom exact du champ
                    "as": "etudiant_info"
                }
            },
            {"$unwind": {"path": "$etudiant_info", "preserveNullAndEmptyArrays": True}},
            
            # Jointure avec administrateurs
            {
                "$lookup": {
                    "from": "administrateurs",
                    "localField": "idadmin_str",
                    "foreignField": "cinadm",   # Vérifier le nom exact du champ
                    "as": "admin_info"
                }
            },
            {"$unwind": {"path": "$admin_info", "preserveNullAndEmptyArrays": True}},
            
            # Jointure avec livres
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv_str",
                    "foreignField": "codliv",    # Vérifier le nom exact du champ
                    "as": "livre_info"
                }
            },
            {"$unwind": {"path": "$livre_info", "preserveNullAndEmptyArrays": True}},
            
            # Projection finale avec gestion des valeurs nulles
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "etudiant": {
                        "$ifNull": [
                            {
                                "nom": "$etudiant_info.nometd",
                                "prenom": "$etudiant_info.prenometd"
                            },
                            {"erreur": "Étudiant non trouvé"}
                        ]
                    },
                    "admin": {
                        "$ifNull": [
                            {
                                "nom": "$admin_info.nomadm",
                                "prenom": "$admin_info.prenomadm"
                            },
                            {"erreur": "Admin non trouvé"}
                        ]
                    },
                    "livre": {
                        "$ifNull": [
                            {
                                "titre": "$livre_info.titreliv",
                                "auteur": "$livre_info.nomaut"
                            },
                            {"erreur": "Livre non trouvé"}
                        ]
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


    try:
        pipeline = [
            # Jointure avec les étudiants
            {
                "$lookup": {
                    "from": "etudiants",
                    "localField": "idetudiant",
                    "foreignField": "cne_etd",
                    "as": "etudiant_info"
                }
            },
            # Jointure avec les administrateurs
            {
                "$lookup": {
                    "from": "administrateurs",
                    "localField": "idadmin",
                    "foreignField": "cinadm",
                    "as": "admin_info"
                }
            },
            # Jointure avec les livres
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            # Projection finale
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "etudiant": {
                        "nom": {"$arrayElemAt": ["$etudiant_info.nometd", 0]},
                        "prenom": {"$arrayElemAt": ["$etudiant_info.prenometd", 0]}
                    },
                    "admin": {
                        "nom": {"$arrayElemAt": ["$admin_info.nomadm", 0]},
                        "prenom": {"$arrayElemAt": ["$admin_info.prenomadm", 0]}
                    },
                    "livre": {
                        "titre": {"$arrayElemAt": ["$livre_info.titreliv", 0]},
                        "auteur": {"$arrayElemAt": ["$livre_info.nomaut", 0]}
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        pipeline = [
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "numero_admin": 1,
                    "idetudiant": 1,
                    "codliv": 1,
                    "dateaccord": {
                        "$dateToString": {
                            "format": "%Y-%m-%dT%H:%M:%S.%LZ",
                            "date": "$dateaccord"
                        }
                    },
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        return jsonify({"prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            {"$unwind": {"path": "$livre_info", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "livre": {
                        "$ifNull": [
                            {
                                "titre": "$livre_info.titreliv",
                                "auteur": "$livre_info.nomaut"
                            },
                            {
                                "$concat": [
                                    "NON TROUVÉ (Code: ",
                                    {"$toString": "$codeliv"},
                                    ")"
                                ]
                            }
                        ]
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            {"$unwind": {"path": "$livre_info", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "debug_codeliv": "$codeliv",  # Log du code livre
                    "livre": {
                        "$ifNull": [
                            {
                                "titre": "$livre_info.titreliv",
                                "auteur": "$livre_info.nomaut"
                            },
                            "NON TROUVÉ (Code: " + {"$toString": "$codeliv"} + ")"
                        ]
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        print("DEBUG - Premier prêt:", prets[0])  # Journalisation
        
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        print("ERREUR CRITIQUE:", str(e))  # Log serveur
        return jsonify({"error": str(e)}), 500
    try:
        pipeline = [
            # Conversion explicite en string
            {
                "$addFields": {
                    "codeliv": {"$toString": "$codeliv"}
                }
            },
            # Jointure avec livres
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv_str",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            {"$unwind": {"path": "$livre_info", "preserveNullAndEmptyArrays": True}},
            # Formatage avec vérification d'erreur
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "livre": {
                        "$cond": [
                            {"$eq": ["$livre_info", {}]},
                            {"erreur": "Code livre invalide", "code": "$codeliv_str"},
                            {
                                "titre": "$livre_info.titreliv",
                                "auteur": "$livre_info.nomaut",
                                "isbn": "$livre_info.codliv"
                            }
                        ]
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]

        prets = list(mongo.db.prets.aggregate(pipeline))
        return jsonify({"count": len(prets), "prets": prets}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    try:
        pipeline = [
            # Conversion explicite en string
            {
                "$addFields": {
                    "codeliv_str": {"$toString": "$codeliv"}
                }
            },
            # Jointure avec livres
            {
                "$lookup": {
                    "from": "livres",
                    "localField": "codeliv_str",
                    "foreignField": "codliv",
                    "as": "livre_info"
                }
            },
            {"$unwind": {"path": "$livre_info", "preserveNullAndEmptyArrays": True}},
            # Formatage avec vérification d'erreur
            {
                "$project": {
                    "_id": 0,
                    "pret_id": {"$toString": "$_id"},
                    "livre": {
                        "$cond": [
                            {"$eq": ["$livre_info", {}]},
                            {"erreur": "Code livre invalide", "code": "$codeliv_str"},
                            {
                                "titre": "$livre_info.titreliv",
                                "auteur": "$livre_info.nomaut",
                                "isbn": "$livre_info.codliv"
                            }
                        ]
                    },
                    "date_emprunt": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateaccord"}},
                    "statut": 1
                }
            }
        ]

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
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

if __name__ == '__main__':
    app.run(debug=True)
