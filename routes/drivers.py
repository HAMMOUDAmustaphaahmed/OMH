from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
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


def create_driver_folder(driver_id):
    folder_path = os.path.join(Config.UPLOAD_FOLDER, f'cahiers/cahier_{driver_id}')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def create_date_folder(driver_id, date):
    base_folder = create_driver_folder(driver_id)
    date_folder = os.path.join(base_folder, date.strftime('%Y-%m-%d'))
    if not os.path.exists(date_folder):
        os.makedirs(date_folder)
    return date_folder

@drivers_bp.route('/edit/<int:driver_id>', methods=['GET', 'POST'])
@login_required
def edit(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    
    if request.method == 'POST':
        try:
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
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)
                    
                    if driver.photo_url and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, driver.photo_url.replace('/static/uploads/', ''))):
                        os.remove(os.path.join(Config.UPLOAD_FOLDER, driver.photo_url.replace('/static/uploads/', '')))
                    
                    driver.photo_url = f'/static/uploads/drivers/{unique_filename}'
            
            # Gestion du type de financement
            type_financement = request.form.get('type_financement')
            if type_financement in ['Commission', 'Salaire Fixe', 'Commission et Salaire Fixe']:
                driver.type_financement = type_financement
                
                # Gestion de la commission
                if type_financement in ['Commission', 'Commission et Salaire Fixe']:
                    commission = request.form.get('pourcentage_commission')
                    driver.pourcentage_commission = float(commission) if commission else None
                else:
                    driver.pourcentage_commission = None
                
                # Gestion du salaire fixe
                if type_financement in ['Salaire Fixe', 'Commission et Salaire Fixe']:
                    salaire = request.form.get('salaire_fixe')
                    driver.salaire_fixe = float(salaire) if salaire else None
                else:
                    driver.salaire_fixe = None
            
            db.session.commit()
            flash('Le chauffeur a été mis à jour avec succès.', 'success')
            return redirect(url_for('drivers.index'))
            
        except ValueError as e:
            db.session.rollback()
            flash('Erreur de validation des données : ' + str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue : ' + str(e), 'danger')
    
    return render_template('drivers/edit.html', driver=driver)


@drivers_bp.route('/cahiers/<int:driver_id>')
@login_required
def list_cahiers(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    cahiers = CahierJournalier.query.filter_by(id_chauffeur=driver_id).order_by(CahierJournalier.date_cahier.desc()).all()
    return render_template('drivers/cahiers.html', driver=driver, cahiers=cahiers)

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


def allowed_cahier_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




import os
from datetime import datetime
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

@drivers_bp.route('/<int:driver_id>/upload-cahier', methods=['POST'])
@login_required
def upload_cahier(driver_id):
    try:
        if 'documents[]' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})

        date_str = request.form.get('date_document')
        if not date_str:
            return jsonify({'success': False, 'message': 'Date requise'})

        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_folder = date_obj.strftime('%d-%m-%Y')

        # Créer le dossier du chauffeur s'il n'existe pas
        driver_folder = os.path.join(Config.UPLOAD_FOLDER, 'cahiers', str(driver_id))
        date_path = os.path.join(driver_folder, date_folder)
        os.makedirs(date_path, exist_ok=True)

        files = request.files.getlist('documents[]')
        uploaded_files = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(date_path, filename)
                
                # Vérifier si le fichier existe déjà
                if os.path.exists(file_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(file_path):
                        filename = f"{base}_{counter}{ext}"
                        file_path = os.path.join(date_path, filename)
                        counter += 1

                file.save(file_path)
                uploaded_files.append(filename)

        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} fichier(s) uploadé(s) avec succès',
            'files': uploaded_files
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@drivers_bp.route('/<int:driver_id>/cahier')
@login_required
def view_cahier(driver_id):
    driver = Chauffeur.query.get_or_404(driver_id)
    cahier_path = os.path.join(Config.UPLOAD_FOLDER, 'cahiers', str(driver_id))
    
    # Structure pour stocker les documents organisés par date
    documents = {}
    
    if os.path.exists(cahier_path):
        for date_folder in sorted(os.listdir(cahier_path), reverse=True):
            folder_path = os.path.join(cahier_path, date_folder)
            if os.path.isdir(folder_path):
                documents[date_folder] = []
                for file in os.listdir(folder_path):
                    file_path = os.path.join('static', 'uploads', 'cahiers', 
                                           str(driver_id), date_folder, file)
                    documents[date_folder].append({
                        'name': file,
                        'path': file_path,
                        'type': 'pdf' if file.lower().endswith('.pdf') else 'image'
                    })
    
    return render_template('drivers/view_cahier.html', 
                         driver=driver, documents=documents)