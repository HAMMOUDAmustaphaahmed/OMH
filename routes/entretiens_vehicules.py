from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from models import db, EntretienVehicule, Vehicule, Notification
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
import os
from werkzeug.utils import secure_filename

entretiens = Blueprint('entretiens', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_maintenance_notifications():
    vehicles = Vehicule.query.all()
    notifications = []
    
    for vehicle in vehicles:
        latest_maintenance = EntretienVehicule.query.filter_by(id_vehicule=vehicle.id_vehicule).order_by(EntretienVehicule.date_entretien.desc()).first()
        
        if latest_maintenance:
            km_actuel = vehicle.kilometrage_vehicule
            km_diff = latest_maintenance.kilometrage_suivant - km_actuel
            
            if km_diff <= 500 and not Notification.query.filter_by(
                id_vehicule=vehicle.id_vehicule,
                id_entretien=latest_maintenance.id_entretien,
                severity='red',
                read=False
            ).first():
                notif = Notification(
                    id_vehicule=vehicle.id_vehicule,
                    id_entretien=latest_maintenance.id_entretien,
                    message=f"URGENT: Entretien nécessaire pour {vehicle.matricule} dans moins de 500 km",
                    severity='red'
                )
                db.session.add(notif)
                
            elif km_diff <= 1000 and not Notification.query.filter_by(
                id_vehicule=vehicle.id_vehicule,
                id_entretien=latest_maintenance.id_entretien,
                severity='yellow',
                read=False
            ).first():
                notif = Notification(
                    id_vehicule=vehicle.id_vehicule,
                    id_entretien=latest_maintenance.id_entretien,
                    message=f"Entretien à prévoir pour {vehicle.matricule} dans moins de 1000 km",
                    severity='yellow'
                )
                db.session.add(notif)
    
    db.session.commit()

@entretiens.route('/')
@login_required
def index():
    check_maintenance_notifications()
    entretiens = EntretienVehicule.query.order_by(EntretienVehicule.date_entretien.desc()).all()
    return render_template('entretiens/manage.html', entretiens=entretiens)

@entretiens.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    vehicules = Vehicule.query.all()
    if request.method == 'POST':
        try:
            pieces = request.form.getlist('pieces[]')
            file = request.files.get('facture')
            facture_url = None
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                facture_url = filename
            
            entretien = EntretienVehicule(
                id_vehicule=request.form['vehicule'],
                type_entretien=request.form['type_entretien'],
                prix_entretien=Decimal(request.form['prix_entretien']),
                date_entretien=datetime.strptime(request.form['date_entretien'], '%Y-%m-%d'),
                kilometrage=float(request.form['kilometrage']),
                kilometrage_suivant=float(request.form['kilometrage_suivant']),
                description=request.form['description'],
                prestataire=request.form['prestataire'],
                facture_reference=request.form['facture_reference'],
                facture_url=facture_url,
                pieces=pieces,
                created_by=current_user.id_user
            )
            
            db.session.add(entretien)
            db.session.commit()
            
            flash('Entretien ajouté avec succès!', 'success')
            return redirect(url_for('entretiens.index'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout de l\'entretien: {str(e)}', 'error')
    
    return render_template('entretiens/add.html', vehicules=vehicules)

@entretiens.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    entretien = EntretienVehicule.query.get_or_404(id)
    vehicules = Vehicule.query.all()
    
    if request.method == 'POST':
        try:
            pieces = request.form.getlist('pieces[]')
            file = request.files.get('facture')
            
            if file and allowed_file(file.filename):
                # Supprimer l'ancienne facture si elle existe
                if entretien.facture_url:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], entretien.facture_url)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                entretien.facture_url = filename
            
            entretien.id_vehicule = request.form['vehicule']
            entretien.type_entretien = request.form['type_entretien']
            entretien.prix_entretien = Decimal(request.form['prix_entretien'])
            entretien.date_entretien = datetime.strptime(request.form['date_entretien'], '%Y-%m-%d')
            entretien.kilometrage = float(request.form['kilometrage'])
            entretien.kilometrage_suivant = float(request.form['kilometrage_suivant'])
            entretien.description = request.form['description']
            entretien.prestataire = request.form['prestataire']
            entretien.facture_reference = request.form['facture_reference']
            entretien.pieces = pieces
            
            db.session.commit()
            check_maintenance_notifications()
            
            flash('Entretien mis à jour avec succès!', 'success')
            return redirect(url_for('entretiens.index'))
        except Exception as e:
            flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
    
    return render_template('entretiens/edit.html', entretien=entretien, vehicules=vehicules)

@entretiens.route('/details/<int:id>')
@login_required
def details(id):
    entretien = EntretienVehicule.query.get_or_404(id)
    return render_template('entretiens/details.html', entretien=entretien)

@entretiens.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    print(f"Tentative de suppression de l'entretien {id}")
    entretien = EntretienVehicule.query.get_or_404(id)
    try:
        # D'abord, supprimer toutes les notifications associées
        Notification.query.filter_by(id_entretien=id).delete()
        
        # Ensuite, supprimer l'entretien
        if entretien.facture_url:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], entretien.facture_url)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(entretien)
        db.session.commit()
        print(f"Suppression réussie de l'entretien {id}")
        flash('Entretien supprimé avec succès!', 'success')
    except Exception as e:
        print(f"Erreur lors de la suppression de l'entretien {id}: {str(e)}")
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    return redirect(url_for('entretiens.index'))

@entretiens.route('/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(read=False).order_by(Notification.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'severity': n.severity,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
    } for n in notifications])

@entretiens.route('/notifications/mark-read/<int:id>')
@login_required
def mark_notification_read(id):
    notification = Notification.query.get_or_404(id)
    notification.read = True
    db.session.commit()
    return jsonify({'success': True})