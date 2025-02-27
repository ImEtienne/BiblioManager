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
        user = User.get_user_by_username(mongo, username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
    return render_template('login.html')

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('auth_routes.login'))
