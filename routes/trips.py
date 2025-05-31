from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Trip, TripDepense, VenteTrip
from sqlalchemy import extract
from datetime import datetime
import pandas as pd

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

@trips_bp.route('/')
@login_required
def index():
    return render_template('trips/manage.html')

@trips_bp.route('/data')
@login_required
def get_trips_data():
    # Récupération des paramètres de filtrage
    search = request.args.get('search', '')
    trip_type = request.args.get('type', '')
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    
    # Construction de la requête
    query = Trip.query
    
    if search:
        query = query.filter(
            db.or_(
                Trip.code.ilike(f'%{search}%'),
                Trip.nom.ilike(f'%{search}%'),
                Trip.client_nom.ilike(f'%{search}%')
            )
        )
    
    if trip_type:
        query = query.filter(Trip.type == trip_type)
        
    if date_start:
        date_start = datetime.strptime(date_start, '%Y-%m-%d')
        query = query.filter(Trip.date_depart >= date_start)
        
    if date_end:
        date_end = datetime.strptime(date_end, '%Y-%m-%d')
        query = query.filter(Trip.date_depart <= date_end)
    
    # Récupération des voyages
    trips = query.all()
    
    # Formatage des données pour le tableau
    data = [{
        'id': trip.id,
        'code': trip.code,
        'nom': trip.nom,
        'type': trip.type,
        'client': trip.client_nom,
        'date_depart': trip.date_depart.strftime('%Y-%m-%d %H:%M'),
        'total_passagers': trip.total_passagers,
        'tarif': float(trip.tarif),
        'vehicules': [v.matricule for v in trip.vehicules],
        'chauffeurs': [f"{c.prenom} {c.nom}" for c in trip.chauffeurs]
    } for trip in trips]
    
    return jsonify(data)

@trips_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # Création du voyage
        trip = Trip(
            nom=request.form['nom'],
            type=request.form['type'],
            client_nom=request.form['client_nom'],
            client_telephone=request.form.get('client_telephone'),
            client_email=request.form.get('client_email'),
            date_depart=datetime.strptime(
                f"{request.form['date']} {request.form['heure']}", 
                '%Y-%m-%d %H:%M'
            ),
            total_passagers=int(request.form['total_passagers']),
            nombre_adultes=int(request.form['nombre_adultes']),
            nombre_enfants=int(request.form['nombre_enfants']),
            nombre_bebes=int(request.form['nombre_bebes']),
            tarif=float(request.form['tarif']),
            commission_achat=bool(request.form.get('commission_achat')),
            montant_commission=float(request.form.get('montant_commission', 0)),
            point_depart=request.form['point_depart'],
            point_arrivee=request.form['point_arrivee'],
            points_intermediaires=request.form.getlist('points_intermediaires'),
            retour_vide=bool(request.form.get('retour_vide')),
            created_by_id=current_user.id
        )
        
        # Ajout des véhicules
        vehicule_ids = request.form.getlist('vehicules')
        for vid in vehicule_ids:
            vehicule = Vehicule.query.get(vid)
            trip.vehicules.append(vehicule)
            
        # Ajout des chauffeurs
        chauffeur_ids = request.form.getlist('chauffeurs')
        for cid in chauffeur_ids:
            chauffeur = Chauffeur.query.get(cid)
            trip.chauffeurs.append(chauffeur)
            
        # Ajout des dépenses si excursion
        if trip.type in ['Excursion', 'Varié']:
            depenses = request.form.getlist('depense_nom')
            montants = request.form.getlist('depense_montant')
            
            for nom, montant in zip(depenses, montants):
                if nom and montant:
                    depense = TripDepense(
                        nom=nom,
                        montant=float(montant)
                    )
                    trip.depenses.append(depense)
        
        db.session.add(trip)
        db.session.commit()
        
        return redirect(url_for('trips.index'))
        
    return render_template(
        'trips/add.html',
        vehicules=Vehicule.query.filter_by(etat='En marche').all(),
        chauffeurs=Chauffeur.query.filter_by(statut='Actif').all()
    )

@trips_bp.route('/edit/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def edit(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        trip.nom = request.form['nom']
        trip.type = request.form['type']
        trip.client_nom = request.form['client_nom']
        trip.client_telephone = request.form.get('client_telephone')
        trip.client_email = request.form.get('client_email')
        trip.date_depart = datetime.strptime(
            f"{request.form['date']} {request.form['heure']}", 
            '%Y-%m-%d %H:%M'
        )
        trip.total_passagers = int(request.form['total_passagers'])
        trip.nombre_adultes = int(request.form['nombre_adultes'])
        trip.nombre_enfants = int(request.form['nombre_enfants'])
        trip.nombre_bebes = int(request.form['nombre_bebes'])
        trip.tarif = float(request.form['tarif'])
        trip.commission_achat = bool(request.form.get('commission_achat'))
        trip.montant_commission = float(request.form.get('montant_commission', 0))
        trip.point_depart = request.form['point_depart']
        trip.point_arrivee = request.form['point_arrivee']
        trip.points_intermediaires = request.form.getlist('points_intermediaires')
        trip.retour_vide = bool(request.form.get('retour_vide'))
        
        # Mise à jour des véhicules
        trip.vehicules = []
        vehicule_ids = request.form.getlist('vehicules')
        for vid in vehicule_ids:
            vehicule = Vehicule.query.get(vid)
            trip.vehicules.append(vehicule)
            
        # Mise à jour des chauffeurs
        trip.chauffeurs = []
        chauffeur_ids = request.form.getlist('chauffeurs')
        for cid in chauffeur_ids:
            chauffeur = Chauffeur.query.get(cid)
            trip.chauffeurs.append(chauffeur)
            
        # Mise à jour des dépenses
        if trip.type in ['Excursion', 'Varié']:
            trip.depenses = []
            depenses = request.form.getlist('depense_nom')
            montants = request.form.getlist('depense_montant')
            
            for nom, montant in zip(depenses, montants):
                if nom and montant:
                    depense = TripDepense(
                        nom=nom,
                        montant=float(montant)
                    )
                    trip.depenses.append(depense)
        
        db.session.commit()
        return redirect(url_for('trips.index'))
    
    return render_template(
        'trips/edit.html',
        trip=trip,
        vehicules=Vehicule.query.filter_by(etat='En marche').all(),
        chauffeurs=Chauffeur.query.filter_by(statut='Actif').all()
    )

@trips_bp.route('/delete/<int:trip_id>', methods=['POST'])
@login_required
def delete(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    return redirect(url_for('trips.index'))

@trips_bp.route('/export')
@login_required
def export():
    trips = Trip.query.all()
    
    data = []
    for trip in trips:
        data.append({
            'Code': trip.code,
            'Nom': trip.nom,
            'Type': trip.type,
            'Client': trip.client_nom,
            'Date départ': trip.date_depart.strftime('%Y-%m-%d %H:%M'),
            'Point départ': trip.point_depart,
            'Point arrivée': trip.point_arrivee,
            'Total passagers': trip.total_passagers,
            'Adultes': trip.nombre_adultes,
            'Enfants': trip.nombre_enfants,
            'Bébés': trip.nombre_bebes,
            'Tarif': float(trip.tarif),
            'Commission': float(trip.montant_commission) if trip.commission_achat else 0,
            'Véhicules': ', '.join(v.matricule for v in trip.vehicules),
            'Chauffeurs': ', '.join(f"{c.prenom} {c.nom}" for c in trip.chauffeurs),
            'Dépenses': sum(float(d.montant) for d in trip.depenses)
        })
    
    df = pd.DataFrame(data)
    filename = f"voyages_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    df.to_excel(f"static/exports/{filename}", index=False)
    
    return jsonify({'url': url_for('static', filename=f'exports/{filename}')})

# Routes pour les ventes
@trips_bp.route('/ventes/add', methods=['GET', 'POST'])
@login_required
def add_vente():
    if request.method == 'POST':
        vente = VenteTrip(
            client_nom=request.form['client_nom'],
            prix=float(request.form['prix']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            created_by_id=current_user.id
        )
        db.session.add(vente)
        db.session.commit()
        return redirect(url_for('trips.index'))
        
    return render_template('trips/vente_trip.html')