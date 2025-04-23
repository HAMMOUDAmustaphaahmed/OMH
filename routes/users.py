from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, db
from functools import wraps

users_bp = Blueprint('users', __name__, url_prefix='/users')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Vous n\'avez pas les permissions nécessaires pour accéder à cette page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('users/manage.html', users=users)

@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        role = request.form.get('role')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        
        # Vérification si le nom d'utilisateur existe déjà
        username = f"{nom.lower()}.{prenom.lower()}"
        if User.query.filter_by(username=username).first():
            flash(f'L\'utilisateur avec le nom d\'utilisateur {username} existe déjà.', 'danger')
            return redirect(url_for('users.add'))
        
        user = User.create_user(nom=nom, prenom=prenom, role=role)
        user.email = email
        user.telephone = telephone
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'L\'utilisateur {user.prenom} {user.nom} a été créé avec succès. Nom d\'utilisateur: {user.username}', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/add.html')

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.nom = request.form.get('nom')
        user.prenom = request.form.get('prenom')
        user.email = request.form.get('email')
        user.telephone = request.form.get('telephone')
        
        # Ne changez le rôle que si l'utilisateur n'est pas l'admin actuel
        if user.id_user != current_user.id_user:
            user.role = request.form.get('role')
            user.actif = 'actif' in request.form
        
        # Réinitialiser le mot de passe si demandé
        if 'reset_password' in request.form:
            default_password = f"{user.nom.lower()}.{user.prenom.lower()}"
            user.set_password(default_password)
            flash(f'Le mot de passe a été réinitialisé à {default_password}', 'info')
        
        db.session.commit()
        flash('L\'utilisateur a été mis à jour avec succès.', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/edit.html', user=user)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    
    # Empêcher la suppression de l'utilisateur actuel
    if user.id_user == current_user.id_user:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('users.index'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('L\'utilisateur a été supprimé avec succès.', 'success')
    return redirect(url_for('users.index'))