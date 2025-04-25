from flask import Blueprint, render_template, flash
from flask_login import current_user, login_required
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required  
def index():
    # Créer le message de bienvenue avec l'heure actuelle
    current_time = datetime.now()
    welcome_message = f"Bienvenue, {current_user.prenom} {current_user.nom} | Rôles: {current_user.role} | {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
    flash(welcome_message, 'welcome')
    return render_template('dashboard.html', user=current_user)