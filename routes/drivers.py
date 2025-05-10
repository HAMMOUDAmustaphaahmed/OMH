from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import Chauffeur,CahierJournalier, db, TripAffectation
from werkzeug.utils import secure_filename
import os
from app import Config
import uuid
from datetime import datetime
from sqlalchemy import func


drivers_bp = Blueprint('drivers', __name__, url_prefix='/drivers')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@drivers_bp.route('/')
@login_required
def index():
    # Obtenir le premier jour du mois courant
    current_date = datetime.now()
    first_day_of_month = datetime(current_date.year, current_date.month, 1)

    # Requête pour obtenir les chauffeurs avec leur nombre de voyages ce mois
    drivers_with_trips = db.session.query(
        Chauffeur,
        func.count(TripAffectation.id_affectation).label('trips_count')
    ).outerjoin(
        TripAffectation,
        (Chauffeur.id_chauffeur == TripAffectation.id_chauffeur)
    ).group_by(
        Chauffeur
    ).all()

    # Convertir les résultats en dictionnaire pour un accès plus facile dans le template
    drivers_data = [
        {
            'driver': driver,
            'trips_count': trips_count
        }
        for driver, trips_count in drivers_with_trips
    ]

    return render_template('drivers/manage.html', drivers=drivers_data)

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
            
            # Get and validate gain percentage
            type_financement = request.form.get('type_financement')
            pourcentage_commission = None
            salaire_fixe = None

            if type_financement in ['Commission', 'Commission et Salaire']:
                pourcentage_commission = float(request.form.get('pourcentage_commission'))
            
            if type_financement in ['Salaire Fixe', 'Commission et Salaire']:
                salaire_fixe = float(request.form.get('salaire_fixe'))
            
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
                notes=request.form.get('notes'),
                type_financement=type_financement,
                pourcentage_commission=pourcentage_commission,
                salaire_fixe=salaire_fixe
            )
            
            # Traitement de la photo...
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
            flash('Erreur dans le format des données. Veuillez vérifier les informations saisies.', 'danger')
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
        


        driver.type_financement = request.form.get('type_financement')
        if driver.type_financement == 'Salaire':
            driver.montant_salaire = request.form.get('montant_salaire')
            driver.taux_commission = None
        elif driver.type_financement == 'Commission':
            driver.taux_commission = request.form.get('taux_commission')
            driver.montant_salaire = None
        else :
            driver.taux_commission = request.form.get('taux_commission')
            driver.montant_salaire = request.form.get('montant_salaire')
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


@drivers_bp.route('/cahier/<int:driver_id>', methods=['GET'])
@login_required
def cahier(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    cahiers = CahierJournalier.query.filter_by(id_chauffeur=driver_id).order_by(CahierJournalier.date_cahier.desc()).all()
    return render_template('drivers/cahier.html', driver=driver, cahiers=cahiers)

@drivers_bp.route('/cahier/<int:driver_id>/upload', methods=['POST'])
@login_required
def upload_cahier(driver_id):
    if 'fichier' not in request.files:
        flash('Aucun fichier n\'a été envoyé.', 'danger')
        return redirect(url_for('drivers.cahier', driver_id=driver_id))
    
    file = request.files['fichier']
    if file.filename == '':
        flash('Aucun fichier sélectionné.', 'danger')
        return redirect(url_for('drivers.cahier', driver_id=driver_id))
    
    try:
        date_cahier = datetime.strptime(request.form.get('date_cahier'), '%Y-%m-%d').date()
        
        # Vérifier si un cahier existe déjà pour cette date
        existing_cahier = CahierJournalier.query.filter_by(
            id_chauffeur=driver_id, 
            date_cahier=date_cahier
        ).first()
        
        if existing_cahier:
            flash('Un cahier existe déjà pour cette date.', 'danger')
            return redirect(url_for('drivers.cahier', driver_id=driver_id))
        
        if file and allowed_cahier_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Créer le dossier pour ce chauffeur s'il n'existe pas
            driver_folder = os.path.join(Config.UPLOAD_FOLDER, 'cahiers', f'chauffeur_{driver_id}')
            date_folder = os.path.join(driver_folder, date_cahier.strftime('%Y-%m-%d'))
            os.makedirs(date_folder, exist_ok=True)
            
            file_path = os.path.join(date_folder, unique_filename)
            file.save(file_path)
            
            # Créer l'entrée dans la base de données
            new_cahier = CahierJournalier(
                id_chauffeur=driver_id,
                date_cahier=date_cahier,
                fichier_url=f'/static/uploads/cahiers/chauffeur_{driver_id}/{date_cahier.strftime("%Y-%m-%d")}/{unique_filename}',
                type_fichier='pdf' if file.filename.endswith('.pdf') else 'image',
                notes=request.form.get('notes')
            )
            
            db.session.add(new_cahier)
            db.session.commit()
            
            flash('Le cahier a été uploadé avec succès.', 'success')
            return redirect(url_for('drivers.cahier', driver_id=driver_id))
    
    except Exception as e:
        flash(f'Une erreur est survenue : {str(e)}', 'danger')
        
    return redirect(url_for('drivers.cahier', driver_id=driver_id))

def allowed_cahier_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS