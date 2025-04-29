from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Trip, Vehicule, Chauffeur, Paiement, db
from datetime import datetime, date, timedelta

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

@trips_bp.route('/')
@login_required
def index():
    trips = Trip.query.order_by(Trip.date_depart.desc()).all()
    return render_template('trips/manage.html', trips=trips)

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Trip, Vehicule, Chauffeur, db
from datetime import datetime

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

@trips_bp.route('/')
@login_required
def index():
    trips = Trip.query.all()
    return render_template('trips/manage.html', trips=trips)

@trips_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            new_trip = Trip(
                type=request.form.get('type'),
                id_vehicule=request.form.get('id_vehicule'),
                id_chauffeur=request.form.get('id_chauffeur'),
                point_depart=request.form.get('point_depart'),
                point_arrivee=request.form.get('point_arrivee'),
                prix=request.form.get('prix'),
                heure_depart=datetime.strptime(request.form.get('heure_depart'), '%H:%M').time(),
                date_depart=datetime.strptime(request.form.get('date_depart'), '%Y-%m-%d').date(),
                client_nom=request.form.get('client_nom'),
                client_telephone=request.form.get('client_telephone'),
                client_email=request.form.get('client_email'),
                nombre_passagers=request.form.get('nombre_passagers'),
                commentaires=request.form.get('commentaires'),
                created_by=current_user.id_user,
                etat_trip=request.form.get('etat_trip', 'Planifié'),
                etat_paiement=request.form.get('etat_paiement', 'Non payé')
            )

            # Champs optionnels
            if request.form.get('distance'):
                new_trip.distance = float(request.form.get('distance'))
            
            if request.form.get('heure_arrivee'):
                new_trip.heure_arrivee = datetime.strptime(request.form.get('heure_arrivee'), '%H:%M').time()
            
            if request.form.get('date_arrivee'):
                new_trip.date_arrivee = datetime.strptime(request.form.get('date_arrivee'), '%Y-%m-%d').date()

            db.session.add(new_trip)
            db.session.commit()
            
            flash('Le voyage a été ajouté avec succès.', 'success')
            return redirect(url_for('trips.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue : {str(e)}', 'danger')
            return redirect(url_for('trips.add'))

    vehicules = Vehicule.query.filter_by(etat='En Marche').all()
    chauffeurs = Chauffeur.query.filter_by(statut='Actif').all()
    
    return render_template('trips/add.html', vehicules=vehicules, chauffeurs=chauffeurs)

@trips_bp.route('/edit/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def edit(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        try:
            # Validation de base
            if not request.form.get('date_depart') or not request.form.get('heure_depart'):
                raise ValueError("La date et l'heure de départ sont requises")

            # Mise à jour des champs
            trip.type = request.form.get('type')
            trip.id_vehicule = int(request.form.get('id_vehicule'))
            trip.id_chauffeur = int(request.form.get('id_chauffeur'))
            trip.point_depart = request.form.get('point_depart')
            trip.point_arrivee = request.form.get('point_arrivee')
            trip.prix = float(request.form.get('prix'))
            trip.heure_depart = datetime.strptime(request.form.get('heure_depart'), '%H:%M').time()
            trip.date_depart = datetime.strptime(request.form.get('date_depart'), '%Y-%m-%d').date()
            trip.client_nom = request.form.get('client_nom')
            trip.client_telephone = request.form.get('client_telephone')
            trip.client_email = request.form.get('client_email')
            trip.nombre_passagers = int(request.form.get('nombre_passagers')) if request.form.get('nombre_passagers') else None
            trip.commentaires = request.form.get('commentaires')
            trip.etat_trip = request.form.get('etat_trip')
            trip.etat_paiement = request.form.get('etat_paiement')

            # Champs optionnels avec validation
            if request.form.get('distance'):
                trip.distance = float(request.form.get('distance'))
            else:
                trip.distance = None
            
            if request.form.get('heure_arrivee'):
                trip.heure_arrivee = datetime.strptime(request.form.get('heure_arrivee'), '%H:%M').time()
            else:
                trip.heure_arrivee = None
            
            if request.form.get('date_arrivee'):
                trip.date_arrivee = datetime.strptime(request.form.get('date_arrivee'), '%Y-%m-%d').date()
            else:
                trip.date_arrivee = None

            db.session.commit()
            flash('Le voyage a été mis à jour avec succès.', 'success')
            return redirect(url_for('trips.index'))
            
        except ValueError as ve:
            db.session.rollback()
            flash(f'Erreur de validation : {str(ve)}', 'danger')
            return redirect(url_for('trips.edit', trip_id=trip_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue : {str(e)}', 'danger')
            return redirect(url_for('trips.edit', trip_id=trip_id))

    vehicules = Vehicule.query.all()
    chauffeurs = Chauffeur.query.all()
    
    return render_template('trips/edit.html', trip=trip, vehicules=vehicules, chauffeurs=chauffeurs)
@trips_bp.route('/details/<int:trip_id>')
@login_required
def details(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    return render_template('trips/details.html', trip=trip)

@trips_bp.route('/delete/<int:trip_id>', methods=['POST'])
@login_required
def delete(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    try:
        db.session.delete(trip)
        db.session.commit()
        flash('Le voyage a été supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Une erreur est survenue : {str(e)}', 'danger')
    
    return redirect(url_for('trips.index'))




@trips_bp.route('/complete/<int:trip_id>', methods=['POST'])
@login_required
def complete(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    trip.etat_trip = 'Terminé'
    if 'kilometrage' in request.form and request.form.get('kilometrage'):
        # Mettre à jour le kilométrage du véhicule
        vehicule = Vehicule.query.get(trip.id_vehicule)
        new_km = float(request.form.get('kilometrage'))
        if new_km > vehicule.kilometrage_vehicule:
            vehicule.kilometrage_vehicule = new_km
    
    db.session.commit()
    
    flash('Le voyage a été marqué comme terminé.', 'success')
    return redirect(url_for('trips.index'))

@trips_bp.route('/cancel/<int:trip_id>', methods=['POST'])
@login_required
def cancel(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    trip.etat_trip = 'Annulé'
    db.session.commit()
    
    flash('Le voyage a été annulé.', 'success')
    return redirect(url_for('trips.index'))


@trips_bp.route('/payment/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def payment(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        # Calculer le montant déjà payé
        total_paye = sum(float(p.montant_paye) for p in trip.paiements)
        nouveau_paiement = float(request.form.get('montant'))
        
        # Vérifier que le nouveau paiement ne dépasse pas le montant restant
        if total_paye + nouveau_paiement > float(trip.prix):
            flash('Le montant du paiement dépasse le montant restant dû.', 'danger')
            return redirect(url_for('trips.payment', trip_id=trip_id))
        
        paiement = Paiement(
            id_trip=trip_id,
            montant_total=trip.prix,
            montant_paye=request.form.get('montant'),
            mode_paiement=request.form.get('mode_paiement'),
            reference_paiement=request.form.get('reference_paiement'),
            recu_par=current_user.id_user,
            notes=request.form.get('notes')
        )
        
        db.session.add(paiement)
        
        # Mise à jour de l'état de paiement du voyage
        if total_paye + nouveau_paiement >= float(trip.prix):
            trip.etat_paiement = 'Payé'
        else:
            trip.etat_paiement = 'Acompte'
        
        db.session.commit()
        
        flash('Le paiement a été enregistré avec succès.', 'success')
        return redirect(url_for('trips.details', trip_id=trip_id))
    
    # Calculer le montant déjà payé
    total_paye = sum(float(p.montant_paye) for p in trip.paiements)
    montant_restant = float(trip.prix) - total_paye
    
    return render_template('trips/payment.html', trip=trip, montant_restant=montant_restant)

@trips_bp.route('/calendar')
@login_required
def calendar():
    return render_template('trips/calendar.html')

@trips_bp.route('/api/calendar-data')
@login_required
def calendar_data():
    start_date = request.args.get('start', date.today().replace(day=1).isoformat())
    end_date = request.args.get('end', (date.today().replace(day=1) + timedelta(days=31)).isoformat())
    
    trips = Trip.query.filter(
        Trip.date_depart.between(start_date, end_date)
    ).all()
    
    events = []
    for trip in trips:
        color = {
            'Planifié': '#3788d8',
            'En cours': '#f8c146',
            'Terminé': '#28a745',
            'Annulé': '#dc3545'
        }.get(trip.etat_trip, '#3788d8')
        
        events.append({
            'id': trip.id_trip,
            'title': f"{trip.client_nom} - {trip.type}",
            'start': f"{trip.date_depart.isoformat()}T{trip.heure_depart.isoformat()}",
            'end': f"{trip.date_arrivee.isoformat() if trip.date_arrivee else trip.date_depart.isoformat()}T{trip.heure_arrivee.isoformat() if trip.heure_arrivee else '23:59:59'}",
            'color': color,
            'url': url_for('trips.details', trip_id=trip.id_trip)
        })
    
    return jsonify(events)