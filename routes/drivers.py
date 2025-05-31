from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import Chauffeur, db
from werkzeug.utils import secure_filename
import os
from app import Config
import uuid
from datetime import datetime

drivers_bp = Blueprint('drivers', __name__, url_prefix='/drivers')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@drivers_bp.route('/')
@login_required
def index():
    drivers = Chauffeur.query.all()
    return render_template('drivers/manage.html', drivers=drivers)

@drivers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        numero_cin = request.form.get('numero_cin')
        
        # Vérifier si le CIN existe déjà
        if Chauffeur.query.filter_by(numero_cin=numero_cin).first():
            flash('Un chauffeur avec ce numéro CIN existe déjà.', 'danger')
            return redirect(url_for('drivers.add'))
        
        try:
            # Traitement sécurisé des dates
            date_naissance = None
            date_expiration_permis = None
            date_embauche = None

            if request.form.get('date_naissance'):
                date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d')
            
            if request.form.get('date_expiration_permis'):
                date_expiration_permis = datetime.strptime(request.form.get('date_expiration_permis'), '%Y-%m-%d')
            
            if request.form.get('date_embauche'):
                date_embauche = datetime.strptime(request.form.get('date_embauche'), '%Y-%m-%d')
            
            new_driver = Chauffeur(
                nom=request.form.get('nom'),
                prenom=request.form.get('prenom'),
                numero_cin=numero_cin,
                date_naissance=date_naissance,
                sexe=request.form.get('sexe'),
                telephone=request.form.get('telephone'),
                telephone_urgence=request.form.get('telephone_urgence'),
                adresse=request.form.get('adresse'),
                email=request.form.get('email'),
                permis=request.form.get('permis'),
                date_expiration_permis=date_expiration_permis,
                date_embauche=date_embauche,
                statut=request.form.get('statut'),
                notes=request.form.get('notes')
            )
            
            # Traitement de la photo
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(Config.UPLOAD_FOLDER, 'drivers', unique_filename)
                    
                    # Créer le dossier s'il n'existe pas
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    file.save(file_path)
                    new_driver.photo_url = f'/static/uploads/drivers/{unique_filename}'
            
            db.session.add(new_driver)
            db.session.commit()
            
            flash('Le chauffeur a été ajouté avec succès.', 'success')
            return redirect(url_for('drivers.index'))
            
        except ValueError as e:
            flash('Erreur dans le format des dates. Veuillez vérifier les dates saisies.', 'danger')
            return redirect(url_for('drivers.add'))
        except Exception as e:
            flash(f'Une erreur est survenue : {str(e)}', 'danger')
            return redirect(url_for('drivers.add'))
    
    return render_template('drivers/add.html')
@drivers_bp.route('/edit/<int:driver_id>', methods=['GET', 'POST'])
@login_required
def edit(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    
    if request.method == 'POST':
        driver.nom = request.form.get('nom')
        driver.prenom = request.form.get('prenom')
        driver.numero_cin = request.form.get('numero_cin')
        driver.date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d')
        driver.sexe = request.form.get('sexe')
        driver.telephone = request.form.get('telephone')
        driver.telephone_urgence = request.form.get('telephone_urgence')
        driver.adresse = request.form.get('adresse')
        driver.email = request.form.get('email')
        driver.permis = request.form.get('permis')
        driver.date_expiration_permis = datetime.strptime(request.form.get('date_expiration_permis'), '%Y-%m-%d')
        driver.date_embauche = datetime.strptime(request.form.get('date_embauche'), '%Y-%m-%d')
        driver.statut = request.form.get('statut')
        driver.notes = request.form.get('notes')
        
        # Traitement de la photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(Config.UPLOAD_FOLDER, 'drivers', unique_filename)
                
                # Créer le dossier s'il n'existe pas
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                
                # Supprimer l'ancienne photo si elle existe
                if driver.photo_url and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, driver.photo_url.replace('/static/uploads/', ''))):
                    os.remove(os.path.join(Config.UPLOAD_FOLDER, driver.photo_url.replace('/static/uploads/', '')))
                
                driver.photo_url = f'/static/uploads/drivers/{unique_filename}'
        
        db.session.commit()
        flash('Le chauffeur a été mis à jour avec succès.', 'success')
        return redirect(url_for('drivers.index'))
    
    return render_template('drivers/edit.html', driver=driver)

@drivers_bp.route('/delete/<int:driver_id>', methods=['POST'])
@login_required
def delete(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    
    # Vérifier si le chauffeur est utilisé dans des voyages
    if driver.trips:
        flash('Ce chauffeur ne peut pas être supprimé car il est associé à des voyages.', 'danger')
        return redirect(url_for('drivers.index'))
    
    # Supprimer la photo si elle existe
    if driver.photo_url and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, driver.photo_url.replace('/static/uploads/', ''))):
        os.remove(os.path.join(Config.UPLOAD_FOLDER, driver.photo_url.replace('/static/uploads/', '')))
    
    db.session.delete(driver)
    db.session.commit()
    
    flash('Le chauffeur a été supprimé avec succès.', 'success')
    return redirect(url_for('drivers.index'))

@drivers_bp.route('/details/<int:driver_id>')
@login_required
def details(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    return render_template('drivers/details.html', driver=driver)