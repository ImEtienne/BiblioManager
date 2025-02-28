# routes/book_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from bson import ObjectId

books_routes = Blueprint('books_routes', __name__, url_prefix='/books')

@books_routes.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        nbrpages = request.form.get('nbrpages')
        year = request.form.get('year')
        
        # Vérification simple
        if not title or not author:
            flash("Le titre et l'auteur sont obligatoires.", "warning")
            return render_template('books_add.html')
        
        mongo = current_app.config['mongo']
        # Insertion dans la collection "books"
        mongo.db.books.insert_one({
            "title": title,
            "author": author,
            "nbrpages": nbrpages,
            "year": year,
            "available": True 
        })
        flash("Livre ajouté avec succès !", "success")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    return render_template('books_add.html')

@books_routes.route('/edit/<book_id>', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    mongo = current_app.config['mongo']
    # Récupération du livre à partir de son ID
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        flash("Livre non trouvé.", "danger")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        nbrpages = request.form.get('nbrpages')
        year = request.form.get('year')
        
        # Validation des champs obligatoires
        if not title or not author:
            flash("Le titre et l'auteur sont obligatoires.", "warning")
            return render_template('books_edit.html', book=book)
        
        # Mise à jour du document dans la collection "books"
        mongo.db.books.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {
                "title": title,
                "author": author,
                "nbrpages": nbrpages,
                "year": year
            }}
        )
        flash("Livre modifié avec succès !", "success")
        return redirect(url_for('dashboard_routes.dashboard_books'))
    
    # En GET, afficher le formulaire pré-rempli avec les données du livre
    return render_template('books_edit.html', book=book)

@books_routes.route('/delete/<book_id>', methods=['POST'])
@login_required
def delete(book_id):
    mongo = current_app.config['mongo']
    result = mongo.db.books.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count:
        flash("Livre supprimé avec succès !", "success")
    else:
        flash("Erreur lors de la suppression du livre.", "danger")
    return redirect(url_for('dashboard_routes.dashboard_books'))


@books_routes.route('/mark_unavailable/<book_id>', methods=['POST'])
@login_required
def mark_unavailable(book_id):
    mongo = current_app.config['mongo']
    result = mongo.db.books.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {"available": False}}
    )
    if result.modified_count:
        flash("Livre marqué comme indisponible.", "success")
    else:
        flash("Erreur lors de la mise à jour du livre.", "danger")
    return redirect(url_for('dashboard_routes.dashboard_books'))


@books_routes.route('/maintenance/<book_id>', methods=['POST'])
@login_required
def mark_maintenance(book_id):
    mongo = current_app.config['mongo']
    result = mongo.db.books.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {"maintenance": True, "available": False}}
    )
    if result.modified_count:
        flash("Le livre est en maintenance.", "success")
    else:
        flash("Erreur lors de la mise en maintenance.", "danger")
    return redirect(url_for('dashboard_routes.dashboard_books'))
