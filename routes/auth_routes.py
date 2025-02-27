# routes/auth_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from werkzeug.security import check_password_hash

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mongo = current_app.config['mongo']
        # Cette méthode utilise désormais la collection "utilisateur"
        user = User.get_user_by_username(mongo, username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect('/dashboard')
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
    return render_template('login.html')

# ------------------------------
# NOUVELLE ROUTE: Inscription / Création de compte
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    mongo = current_app.config['mongo']
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Vérification des champs obligatoires
        if not username or not password or not confirm_password:
            flash("Veuillez remplir tous les champs.", "warning")
            return render_template('register.html')
        # Vérifier la concordance des mots de passe
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "warning")
            return render_template('register.html')
        # Vérifier si l'utilisateur existe déjà
        if User.get_user_by_username(mongo, username):
            flash("Nom d'utilisateur déjà utilisé.", "danger")
            return render_template('register.html')
        # Créer l'utilisateur avec le rôle par défaut "user"
        User.create_user(mongo, username, password, role="user")
        flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('auth_routes.login'))
    return render_template('register.html')

@auth_routes.route('/dashboard')
@login_required
def dashboard():
    # Exemple de récupération de statistiques (à adapter selon votre modèle)
    mongo = current_app.config['mongo']
    stats = {
        'total_books': mongo.db.books.count_documents({}),
        'total_members': mongo.db.members.count_documents({}),
        'active_loans': mongo.db.loans.count_documents({"date_returned": None})
    }
    # Vous pouvez aussi ajouter d'autres stats ou données de graphiques
    return render_template('dashboard.html', stats=stats)

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('auth_routes.login'))
