from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Trip, TripAffectation, TripDepense, Paiement, Vehicule, Chauffeur, db
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

# Liste des voyages avec filtres
@trips_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Filtres
    type_voyage = request.args.get('type')
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    status = request.args.get('status')
    search = request.args.get('search')

    # Construction de la requête
    query = Trip.query

    if type_voyage:
        query = query.filter(Trip.type == type_voyage)
    if date_debut:
        query = query.filter(Trip.date_depart >= datetime.strptime(date_debut, '%Y-%m-%d'))
    if date_fin:
        query = query.filter(Trip.date_depart <= datetime.strptime(date_fin, '%Y-%m-%d'))
    if status:
        query = query.filter(Trip.etat_trip == status)
    if search:
        query = query.filter(or_(
            Trip.nom.ilike(f'%{search}%'),
            Trip.client_nom.ilike(f'%{search}%'),
            Trip.point_depart.ilike(f'%{search}%'),
            Trip.point_arrivee.ilike(f'%{search}%')
        ))

    # Tri
    sort_by = request.args.get('sort_by', 'date_depart')
    order = request.args.get('order', 'desc')
    
    if order == 'desc':
        query = query.order_by(getattr(Trip, sort_by).desc())
    else:
        query = query.order_by(getattr(Trip, sort_by).asc())

    trips = query.paginate(page=page, per_page=per_page)
    return render_template('trips/manage.html', trips=trips)


@trips_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    print('Entered the add route')  # Debug
    if request.method == 'POST':
        try:
            print('Handling POST request')  # Debug

            # Parse dates and times
            print('parsing dates and times')
            try:
                # Handle date and time parsing
                date_depart_str = request.form.get('date_depart')
                date_arrivee_str = request.form.get('date_arrivee')
                print('handle dates and times parsing', date_depart_str, date_arrivee_str)
                
                if not date_depart_str:
                    print('Date de départ is missing')  # Debug
                    flash('La date de départ est requise', 'danger')
                    return redirect(url_for('trips.add'))

                date_depart = datetime.strptime(date_depart_str, '%Y-%m-%dT%H:%M')
                print('date_depart', date_depart)
                date_arrivee = datetime.strptime(date_arrivee_str, '%Y-%m-%dT%H:%M') if date_arrivee_str else None
                print('date_arrivee', date_arrivee)
                
                if date_arrivee and date_arrivee < date_depart:
                    print('Date d\'arrivée is earlier than date de départ')  # Debug
                    flash('La date d\'arrivée doit être postérieure à la date de départ', 'danger')
                    return redirect(url_for('trips.add'))

                # Split into date and time components
                date_depart_date = date_depart.date()
                date_depart_time = date_depart.time()
                date_arrivee_date = date_arrivee.date() if date_arrivee else None
                date_arrivee_time = date_arrivee.time() if date_arrivee else None
                print('Dates and times parsed successfully')  # Debug
                
            except ValueError as e:
                print(f'Date parsing error: {e}')  # Debug
                flash('Format de date invalide. Utilisez le format YYYY-MM-DD HH:MM', 'danger')
                return redirect(url_for('trips.add'))

            # Validate vehicle and driver assignments
            print('Validating vehicle and driver assignments')  # Debug
            vehicules = request.form.getlist('vehicules[]')
            chauffeurs = request.form.getlist('chauffeurs[]')
            print('Vehicles:', vehicules, 'Drivers:', chauffeurs)  # Debug

            if not vehicules or not chauffeurs:
                print('Missing vehicle or driver')  # Debug
                flash('Au moins un véhicule et un chauffeur doivent être sélectionnés', 'danger')
                return redirect(url_for('trips.add'))

            # Validate passenger count
            print('Validating passenger count')  # Debug
            nombre_adultes = int(request.form.get('nombre_adultes', 0))
            nombre_enfants = int(request.form.get('nombre_enfants', 0))
            nombre_bebes = int(request.form.get('nombre_bebes', 0))
            print('Passenger counts:', nombre_adultes, nombre_enfants, nombre_bebes)  # Debug
            
            if (nombre_adultes + nombre_enfants + nombre_bebes) <= 0:
                print('Invalid passenger count')  # Debug
                flash('Le nombre total de passagers doit être supérieur à 0', 'danger')
                return redirect(url_for('trips.add'))

            # Create new trip with all fields
            print('Creating new trip')  # Debug
            new_trip = Trip(
                type=request.form.get('type'),
                nom=request.form.get('nom'),
                is_recurring=bool(request.form.getlist('recurring_days')),
                recurring_days=','.join(request.form.getlist('recurring_days')) if request.form.getlist('recurring_days') else None,
                point_depart=request.form.get('point_depart'),
                point_arrivee=request.form.get('point_arrivee'),
                date_depart=date_depart_date,
                heure_depart=date_depart_time,
                date_arrivee=date_arrivee_date,
                heure_arrivee=date_arrivee_time,
                nombre_jours=request.form.get('nombre_jours', type=int),
                nombre_adultes=nombre_adultes,
                nombre_enfants=nombre_enfants,
                nombre_bebes=nombre_bebes,
                client_nom=request.form.get('client_nom'),
                client_telephone=request.form.get('client_telephone'),
                client_email=request.form.get('client_email'),
                commentaires=request.form.get('commentaires'),
                created_by=current_user.id_user,
                etat_trip='Planifié'
            )
            print('New trip created:', new_trip)  # Debug

            # Handle pricing based on tarification type
            print('Handling pricing logic')  # Debug
            tarification_type = request.form.get('tarification_type')
            print('Tarification type:', tarification_type)  # Debug

            if not tarification_type:
                print('Missing tarification type')  # Debug
                flash('Le type de tarification est requis', 'danger')
                return redirect(url_for('trips.add'))

            if tarification_type == 'achat_revente':
                prix_achat = request.form.get('prix_achat', type=float)
                prix_vente = request.form.get('prix_vente', type=float)
                print('Achat/Revente pricing:', prix_achat, prix_vente)  # Debug
                
                if not prix_achat or not prix_vente:
                    flash('Les prix d\'achat et de vente sont requis pour ce type de tarification', 'danger')
                    return redirect(url_for('trips.add'))
                new_trip.prix_achat = prix_achat
                new_trip.prix_vente = prix_vente
                
            elif tarification_type == 'commission':
                prix_base = request.form.get('prix_base', type=float)
                commission = request.form.get('commission', type=float)
                print('Commission pricing:', prix_base, commission)  # Debug
                
                if not prix_base or not commission:
                    flash('Le prix de base et la commission sont requis pour ce type de tarification', 'danger')
                    return redirect(url_for('trips.add'))
                new_trip.prix_base = prix_base
                new_trip.commission = commission

            # Save trip
            print('Saving trip to database')  # Debug
            db.session.add(new_trip)
            db.session.flush()
            print('Trip saved, ID:', new_trip.id_trip)  # Debug

            # Handle additional logic (assignments, expenses, payments, etc.)
            print('Handling additional logic')  # Debug
            # Add your additional logic here.

            # Commit transaction
            db.session.commit()
            print('Transaction committed')  # Debug
            flash('Le voyage a été ajouté avec succès.', 'success')
            return redirect(url_for('trips.details', trip_id=new_trip.id_trip))

        except Exception as e:
            print(f'Error occurred: {e}')  # Debug
            db.session.rollback()
            flash(f'Une erreur est survenue : {str(e)}', 'danger')
            return redirect(url_for('trips.add'))

    print('Handling GET request')  # Debug
    # GET request
    current_date = datetime.utcnow()
    vehicules = Vehicule.query.filter_by(etat='En marche').order_by(Vehicule.modele).all()
    chauffeurs = Chauffeur.query.filter_by(statut='Actif').order_by(Chauffeur.nom).all()
    
    print('Rendering add.html template')  # Debug
    return render_template('trips/add.html', 
                         vehicules=vehicules, 
                         chauffeurs=chauffeurs,
                         current_date=current_date,
                         utcnow=datetime.utcnow())
# Détails d'un voyage
@trips_bp.route('/<int:trip_id>')
@login_required
def details(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    # Récupérer les affectations avec les détails des véhicules et chauffeurs
    affectations = db.session.query(
        TripAffectation, Vehicule, Chauffeur
    ).join(
        Vehicule, TripAffectation.id_vehicule == Vehicule.id_vehicule
    ).join(
        Chauffeur, TripAffectation.id_chauffeur == Chauffeur.id_chauffeur
    ).filter(
        TripAffectation.id_trip == trip_id
    ).all()

    # Récupérer les dépenses
    depenses = TripDepense.query.filter_by(id_trip=trip_id).all()
    
    # Récupérer les paiements
    paiements = Paiement.query.filter_by(id_trip=trip_id).order_by(Paiement.date_paiement.desc()).all()

    return render_template('trips/details.html', 
                         trip=trip, 
                         affectations=affectations, 
                         depenses=depenses, 
                         paiements=paiements)

# Modifier un voyage
@trips_bp.route('/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        try:
            # Mise à jour des informations de base
            trip.type = request.form.get('type')
            trip.nom = request.form.get('nom')
            trip.is_recurring = bool(request.form.getlist('recurring_days'))
            trip.recurring_days = ','.join(request.form.getlist('recurring_days')) if request.form.getlist('recurring_days') else None
            trip.point_depart = request.form.get('point_depart')
            trip.point_arrivee = request.form.get('point_arrivee')
            trip.date_depart = datetime.strptime(request.form.get('date_depart'), '%Y-%m-%d').date()
            trip.heure_depart = datetime.strptime(request.form.get('heure_depart'), '%H:%M').time() if request.form.get('heure_depart') else None
            
            if request.form.get('date_arrivee'):
                trip.date_arrivee = datetime.strptime(request.form.get('date_arrivee'), '%Y-%m-%d').date()
            if request.form.get('heure_arrivee'):
                trip.heure_arrivee = datetime.strptime(request.form.get('heure_arrivee'), '%H:%M').time()
            
            trip.nombre_jours = request.form.get('nombre_jours', type=int)
            trip.nombre_adultes = request.form.get('nombre_adultes', 0, type=int)
            trip.nombre_enfants = request.form.get('nombre_enfants', 0, type=int)
            trip.nombre_bebes = request.form.get('nombre_bebes', 0, type=int)
            
            # Mise à jour des prix
            if request.form.get('tarification_type') == 'achat_revente':
                trip.prix_achat = request.form.get('prix_achat', type=float)
                trip.prix_vente = request.form.get('prix_vente', type=float)
                trip.is_commission = False
                trip.commission = None
            else:
                trip.commission = request.form.get('commission', type=float)
                trip.is_commission = True
                trip.prix_achat = None
                trip.prix_vente = None
            
            # Mise à jour des affectations
            TripAffectation.query.filter_by(id_trip=trip.id_trip).delete()
            
            vehicules = request.form.getlist('vehicules[]')
            chauffeurs = request.form.getlist('chauffeurs[]')
            
            for vehicule_id, chauffeur_id in zip(vehicules, chauffeurs):
                if vehicule_id and chauffeur_id:
                    affectation = TripAffectation(
                        id_trip=trip.id_trip,
                        id_vehicule=vehicule_id,
                        id_chauffeur=chauffeur_id
                    )
                    db.session.add(affectation)
            
            # Mise à jour des dépenses
            TripDepense.query.filter_by(id_trip=trip.id_trip).delete()
            
            if request.form.getlist('depense_nom[]'):
                noms = request.form.getlist('depense_nom[]')
                prix_unitaires = request.form.getlist('depense_prix_unitaire[]')
                nombres_personnes = request.form.getlist('depense_nombre_personnes[]')
                
                for nom, prix, nombre in zip(noms, prix_unitaires, nombres_personnes):
                    if nom and prix and nombre:
                        depense = TripDepense(
                            id_trip=trip.id_trip,
                            nom=nom,
                            prix_unitaire=float(prix),
                            nombre_personnes=int(nombre),
                            total=float(prix) * int(nombre)
                        )
                        db.session.add(depense)
            
            # Mise à jour des informations client
            trip.client_nom = request.form.get('client_nom')
            trip.client_telephone = request.form.get('client_telephone')
            trip.client_email = request.form.get('client_email')
            trip.commentaires = request.form.get('commentaires')
            
            # Mise à jour du paiement si changé
            nouveau_statut_paiement = request.form.get('etat_paiement')
            if nouveau_statut_paiement != trip.etat_paiement:
                if nouveau_statut_paiement == 'Chèque':
                    paiement = Paiement(
                        id_trip=trip.id_trip,
                        mode_paiement='Chèque',
                        montant_total=trip.prix_vente if trip.prix_vente else 0,
                        montant_paye=trip.prix_vente if trip.prix_vente else 0,
                        banque=request.form.get('banque'),
                        numero_cheque=request.form.get('numero_cheque'),
                        recu_par=current_user.id_user
                    )
                    
                    if 'image_cheque' in request.files:
                        file = request.files['image_cheque']
                        if file and file.filename:
                            filename = secure_filename(f"{trip.id_trip}_{file.filename}")
                            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cheques', filename)
                            file.save(filepath)
                            paiement.image_cheque = f'cheques/{filename}'
                    
                    db.session.add(paiement)
                
                trip.etat_paiement = nouveau_statut_paiement

            db.session.commit()
            flash('Le voyage a été mis à jour avec succès.', 'success')
            return redirect(url_for('trips.details', trip_id=trip.id_trip))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue lors de la mise à jour : {str(e)}', 'danger')
            return redirect(url_for('trips.edit', trip_id=trip.id_trip))
    
    # GET request
    vehicules = Vehicule.query.filter_by(etat='En marche').all()
    chauffeurs = Chauffeur.query.filter_by(statut='Actif').all()
    affectations = TripAffectation.query.filter_by(id_trip=trip.id_trip).all()
    depenses = TripDepense.query.filter_by(id_trip=trip.id_trip).all()
    
    return render_template('trips/edit.html', 
                         trip=trip,
                         vehicules=vehicules,
                         chauffeurs=chauffeurs,
                         affectations=affectations,
                         depenses=depenses)

# Supprimer un voyage
@trips_bp.route('/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    try:
        # Supprimer les fichiers associés (images de chèques, etc.)
        for paiement in trip.paiements:
            if paiement.image_cheque:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], paiement.image_cheque))
                except OSError:
                    pass

        # Supprimer le voyage (les suppressions en cascade doivent être configurées dans les modèles)
        db.session.delete(trip)
        db.session.commit()
        flash('Le voyage a été supprimé avec succès.', 'success')
        return redirect(url_for('trips.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Une erreur est survenue lors de la suppression : {str(e)}', 'danger')
        return redirect(url_for('trips.details', trip_id=trip_id))

# Gérer le statut d'un voyage
@trips_bp.route('/<int:trip_id>/status', methods=['POST'])
@login_required
def manage_status(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    new_status = request.form.get('status')
    
    if new_status in ['Planifié', 'En cours', 'Terminé', 'Annulé']:
        try:
            trip.etat_trip = new_status
            db.session.commit()
            flash(f'Le statut du voyage a été mis à jour en "{new_status}".', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue lors de la mise à jour du statut : {str(e)}', 'danger')
    else:
        flash('Statut invalide.', 'danger')
    
    return redirect(url_for('trips.details', trip_id=trip_id))

# API endpoints pour les opérations AJAX
@trips_bp.route('/api/check-availability', methods=['POST'])
@login_required
def check_availability():
    date = request.json.get('date')
    vehicule_id = request.json.get('vehicule_id')
    chauffeur_id = request.json.get('chauffeur_id')
    
    # Vérifier la disponibilité
    conflicts = Trip.query.join(TripAffectation).filter(
        Trip.date_depart == datetime.strptime(date, '%Y-%m-%d').date(),
        or_(
            TripAffectation.id_vehicule == vehicule_id,
            TripAffectation.id_chauffeur == chauffeur_id
        )
    ).all()
    
    return jsonify({
        'available': len(conflicts) == 0,
        'conflicts': [{
            'id': c.id_trip,
            'type': c.type,
            'nom': c.nom
        } for c in conflicts]
    })

# Export des données
@trips_bp.route('/export')
@login_required
def export_data():
    format_type = request.args.get('format', 'excel')
    if format_type == 'excel':
        # Logique d'export Excel
        pass
    elif format_type == 'pdf':
        # Logique d'export PDF
        pass
    return redirect(url_for('trips.index'))