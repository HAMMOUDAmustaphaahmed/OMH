from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password==password:
            if not user.actif:
                flash('Ce compte a été désactivé.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.derniere_connexion = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
            
            flash(f'Bienvenue, {user.prenom} {user.nom}!', 'success')
            return redirect(next_page)
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if current_user.check_password(request.form.get('current_password')):
            current_user.nom = request.form.get('nom')
            current_user.prenom = request.form.get('prenom')
            current_user.email = request.form.get('email')
            current_user.telephone = request.form.get('telephone')
            
            if request.form.get('new_password'):
                current_user.set_password(request.form.get('new_password'))
            
            db.session.commit()
            flash('Votre profil a été mis à jour.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Mot de passe actuel incorrect.', 'danger')
    
    return render_template('dashboard.html')
