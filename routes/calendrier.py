from flask import Blueprint, render_template, jsonify
from models import Trip, Vehicule, Chauffeur, TripAffectation, db
from datetime import datetime

calendrier_bp = Blueprint('calendrier', __name__, url_prefix='/calendrier')

@calendrier_bp.route('/')
def afficher_calendrier():
    # Récupérer tous les voyages avec les relations chauffeur et véhicule via TripAffectation
    trips = db.session.query(Trip)\
        .join(TripAffectation, Trip.id_trip == TripAffectation.id_trip)\
        .join(Vehicule, TripAffectation.id_vehicule == Vehicule.id_vehicule)\
        .join(Chauffeur, TripAffectation.id_chauffeur == Chauffeur.id_chauffeur)\
        .all()
    
    # Transformer les voyages en format JSON compatible avec FullCalendar
    voyages = []
    for trip in trips:
        # Format the date as string
        start_date = trip.date_depart.strftime('%Y-%m-%d')

        # Create event object
        event = {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': start_date,
            'description': f"""
                <strong>Client:</strong> {trip.client_nom or 'Non spécifié'}<br>
                <strong>Téléphone:</strong> {trip.client_telephone or 'Non spécifié'}<br>
                <strong>Chauffeurs:</strong> {', '.join([f"{c.nom} {c.prenom}" for c in trip.chauffeurs]) if trip.chauffeurs else 'Non assigné'}<br>
                <strong>Véhicules:</strong> {', '.join([f"{v.matricule} - {v.modele}" for v in trip.vehicules]) if trip.vehicules else 'Non assigné'}<br>
                <strong>Adultes:</strong> {trip.nombre_adultes or 0}<br>
                <strong>Enfants:</strong> {trip.nombre_enfants or 0}<br>
                <strong>Bébés:</strong> {trip.nombre_bebes or 0}<br>
            """.strip(),
            
            'allDay': True  # Set to true since we're not using time
        }
        voyages.append(event)
    
    return render_template('calendrier.html', voyages=voyages)

@calendrier_bp.route('/api/voyages', methods=['GET'])
def api_voyages():
    # Récupérer tous les voyages avec les relations
    trips = db.session.query(Trip)\
        .join(TripAffectation, Trip.id_trip == TripAffectation.id_trip)\
        .join(Vehicule, TripAffectation.id_vehicule == Vehicule.id_vehicule)\
        .join(Chauffeur, TripAffectation.id_chauffeur == Chauffeur.id_chauffeur)\
        .all()
        
    voyages = []
    for trip in trips:
        # Format the date as string
        start_date = trip.date_depart.strftime('%Y-%m-%d')
        end_date = trip.date_arrivee.strftime('%Y-%m-%d') if trip.date_arrivee else None

        # Create event object
        event = {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': start_date,
            'end': end_date,
            'description': f"""
                <strong>Client:</strong> {trip.client_nom or 'Non spécifié'}<br>
                <strong>Téléphone:</strong> {trip.client_telephone or 'Non spécifié'}<br>
                <strong>Chauffeurs:</strong> {', '.join([f"{c.nom} {c.prenom}" for c in trip.chauffeurs]) if trip.chauffeurs else 'Non assigné'}<br>
                <strong>Véhicules:</strong> {', '.join([f"{v.matricule} - {v.modele}" for v in trip.vehicules]) if trip.vehicules else 'Non assigné'}<br>
                <strong>Adultes:</strong> {trip.nombre_adultes or 0}<br>
                <strong>Enfants:</strong> {trip.nombre_enfants or 0}<br>
                <strong>Bébés:</strong> {trip.nombre_bebes or 0}<br>
                <strong>Prix:</strong> {float(trip.prix_vente) if trip.prix_vente else 0} DT
            """.strip(),
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' 
                             else '#28a745' if trip.etat_trip == 'En cours' 
                             else '#dc3545' if trip.etat_trip == 'Annulé'
                             else '#ffc107',  # Pour 'Terminé'
            'allDay': True  # Set to true since we're not using time
        }
        voyages.append(event)

    return jsonify(voyages)