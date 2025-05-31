from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Vehicule, EntretienVehicule, db
from werkzeug.utils import secure_filename
import os
from app import Config
import uuid
from datetime import datetime

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@vehicles_bp.route('/')
@login_required
def index():
    vehicles = Vehicule.query.all()
    return render_template('vehicles/manage.html', vehicles=vehicles)

@vehicles_bp.route('/<int:vehicle_id>')
@login_required
def details(vehicle_id):
    vehicle = Vehicule.query.get_or_404(vehicle_id)
    return render_template('vehicles/details.html', vehicle=vehicle)


@vehicles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        matricule = request.form.get('matricule')
        
        # Vérifier si la matricule existe déjà
        if Vehicule.query.filter_by(matricule=matricule).first():
            flash('Un véhicule avec cette matricule existe déjà.', 'danger')
            return redirect(url_for('vehicles.add'))
        
        new_vehicle = Vehicule(
            matricule=matricule,
            usine=request.form.get('usine'),
            modele=request.form.get('modele'),
            nombre_place=request.form.get('nombre_place'),
            carburant=request.form.get('carburant'),
            kilometrage_vehicule=request.form.get('kilometrage_vehicule'),
            couleur=request.form.get('couleur'),
            puissance=request.form.get('puissance'),
            prix_achat=request.form.get('prix_achat'),
            etat=request.form.get('etat'),
            annee_fabrication=request.form.get('annee_fabrication'),
            notes=request.form.get('notes')
        )
        
        # Convertir les dates si présentes
        if request.form.get('date_acquisition'):
            new_vehicle.date_acquisition = datetime.strptime(request.form.get('date_acquisition'), '%Y-%m-%d')
        
        if request.form.get('assurance_expiration'):
            new_vehicle.assurance_expiration = datetime.strptime(request.form.get('assurance_expiration'), '%Y-%m-%d')
        
        if request.form.get('inspection_expiration'):
            new_vehicle.inspection_expiration = datetime.strptime(request.form.get('inspection_expiration'), '%Y-%m-%d')
        
        # Traitement de l'image
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(Config.UPLOAD_FOLDER, 'vehicles', unique_filename)
                
                # Créer le dossier s'il n'existe pas
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                new_vehicle.image_url = f'/static/uploads/vehicles/{unique_filename}'
        
        db.session.add(new_vehicle)
        db.session.commit()
        
        flash('Le véhicule a été ajouté avec succès.', 'success')
        return redirect(url_for('vehicles.index'))
    
    return render_template('vehicles/add.html')

@vehicles_bp.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit(vehicle_id):
    vehicle = Vehicule.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        vehicle.matricule = request.form.get('matricule')
        vehicle.usine = request.form.get('usine')
        vehicle.modele = request.form.get('modele')
        vehicle.nombre_place = request.form.get('nombre_place')
        vehicle.carburant = request.form.get('carburant')
        vehicle.kilometrage_vehicule = request.form.get('kilometrage_vehicule')
        vehicle.couleur = request.form.get('couleur')
        vehicle.puissance = request.form.get('puissance')
        vehicle.prix_achat = request.form.get('prix_achat')
        vehicle.etat = request.form.get('etat')
        vehicle.annee_fabrication = request.form.get('annee_fabrication')
        vehicle.notes = request.form.get('notes')
        
        # Convertir les dates si présentes
        if request.form.get('date_acquisition'):
            vehicle.date_acquisition = datetime.strptime(request.form.get('date_acquisition'), '%Y-%m-%d')
        
        if request.form.get('assurance_expiration'):
            vehicle.assurance_expiration = datetime.strptime(request.form.get('assurance_expiration'), '%Y-%m-%d')
        
        if request.form.get('inspection_expiration'):
            vehicle.inspection_expiration = datetime.strptime(request.form.get('inspection_expiration'), '%Y-%m-%d')
        
        # Traitement de l'image
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(Config.UPLOAD_FOLDER, 'vehicles', unique_filename)
                
                # Créer le dossier s'il n'existe pas
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                
                # Supprimer l'ancienne image si elle existe
                if vehicle.image_url and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, vehicle.image_url.replace('/static/uploads/', ''))):
                    os.remove(os.path.join(Config.UPLOAD_FOLDER, vehicle.image_url.replace('/static/uploads/', '')))
                
                vehicle.image_url = f'/static/uploads/vehicles/{unique_filename}'
        
        db.session.commit()
        flash('Le véhicule a été mis à jour avec succès.', 'success')
        return redirect(url_for('vehicles.index'))
    
    return render_template('vehicles/edit.html', vehicle=vehicle)

@vehicles_bp.route('/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete(vehicle_id):
    vehicle = Vehicule.query.get_or_404(vehicle_id)
    
    # Vérifier si le véhicule est utilisé dans des voyages
    if vehicle.trips:
        flash('Ce véhicule ne peut pas être supprimé car il est associé à des voyages.', 'danger')
        return redirect(url_for('vehicles.index'))
    
    # Supprimer l'image si elle existe
    if vehicle.image_url and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, vehicle.image_url.replace('/static/uploads/', ''))):
        os.remove(os.path.join(Config.UPLOAD_FOLDER, vehicle.image_url.replace('/static/uploads/', '')))
    
    db.session.delete(vehicle)
    db.session.commit()
    
    flash('Le véhicule a été supprimé avec succès.', 'success')
    return redirect(url_for('vehicles.index'))

@vehicles_bp.route('/maintenance/<int:vehicle_id>', methods=['GET'])
@login_required
def maintenance_history(vehicle_id):
    vehicle = Vehicule.query.get_or_404(vehicle_id)
    maintenances = EntretienVehicule.query.filter_by(id_vehicule=vehicle_id).order_by(EntretienVehicule.date_entretien.desc()).all()
    
    return render_template('vehicles/maintenance_history.html', vehicle=vehicle, maintenances=maintenances)

@vehicles_bp.route('/maintenance/add/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def add_maintenance(vehicle_id):
    vehicle = Vehicule.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        new_maintenance = EntretienVehicule(
            id_vehicule=vehicle_id,
            type_entretien=request.form.get('type_entretien'),
            prix_entretien=request.form.get('prix_entretien'),
            date_entretien=datetime.strptime(request.form.get('date_entretien'), '%Y-%m-%d'),
            kilometrage=request.form.get('kilometrage'),
            description=request.form.get('description'),
            prestataire=request.form.get('prestataire'),
            facture_reference=request.form.get('facture_reference'),
            created_by=current_user.id_user
        )
        
        if request.form.get('date_prochaine_maintenance'):
            new_maintenance.date_prochaine_maintenance = datetime.strptime(request.form.get('date_prochaine_maintenance'), '%Y-%m-%d')
        
        db.session.add(new_maintenance)
        
        # Mettre à jour le kilométrage du véhicule s'il est supérieur
        if float(request.form.get('kilometrage')) > vehicle.kilometrage_vehicule:
            vehicle.kilometrage_vehicule = float(request.form.get('kilometrage'))
        
        db.session.commit()
        
        flash('L\'entretien a été ajouté avec succès.', 'success')
        return redirect(url_for('vehicles.maintenance_history', vehicle_id=vehicle_id))
    
    return render_template('vehicles/add_maintenance.html', vehicle=vehicle)
