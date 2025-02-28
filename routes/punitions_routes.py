from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from flask import current_app
from bson import ObjectId
import logging

punitions_routes = Blueprint('punitions_routes', __name__)

@punitions_routes.route('/punitions')
@login_required
def punitions():
    try:
        mongo = current_app.config['mongo']
        punitions = list(mongo.db.punition.find().limit(100))  # Limite pour la démo
        return render_template('punitions.html', punitions=punitions)
    
    except Exception as e:
        logging.error(f"Erreur route punitions: {str(e)}")
        return render_template('error.html', message="Erreur de chargement des punitions"), 500



        results = list(mongo.db.etudiants.aggregate(pipeline))
        return jsonify({"punished_students": results}), 200

    except Exception as e:
        logging.critical(f"Erreur aggregation punitions: {str(e)}")
        return jsonify({"error": "Erreur de traitement des données"}), 500