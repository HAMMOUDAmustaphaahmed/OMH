from flask import Blueprint, render_template, jsonify
from models import Trip, Vehicule, Chauffeur, db

calendrier_bp = Blueprint('calendrier', __name__, url_prefix='/calendrier')

@calendrier_bp.route('/')
def afficher_calendrier():
    # Récupérer tous les voyages avec les relations chauffeur et véhicule
    trips = db.session.query(Trip)\
        .join(Vehicule, Trip.id_vehicule == Vehicule.id_vehicule)\
        .join(Chauffeur, Trip.id_chauffeur == Chauffeur.id_chauffeur)\
        .all()
    
    # Transformer les voyages en format JSON compatible avec FullCalendar
    voyages = [
        {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': f"{trip.date_depart}T{trip.heure_depart}",
            'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
            'description': f"""
                <strong>Client:</strong> {trip.client_nom}<br>
                <strong>Téléphone:</strong> {trip.client_telephone}<br>
                <strong>Chauffeur:</strong> {trip.chauffeur.nom} {trip.chauffeur.prenom}<br>
                <strong>Véhicule:</strong> {trip.vehicule.matricule} - {trip.vehicule.modele}<br>
                <strong>Passagers:</strong> {trip.nombre_passagers}<br>
                <strong>Prix:</strong> {trip.prix}€
            """.strip(),
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' else '#28a745' if trip.etat_trip == 'En cours' else '#dc3545'
        }
        for trip in trips
    ]
    
    return render_template('calendrier.html', voyages=voyages)

@calendrier_bp.route('/api/voyages', methods=['GET'])
def api_voyages():
    trips = db.session.query(Trip)\
        .join(Vehicule, Trip.id_vehicule == Vehicule.id_vehicule)\
        .join(Chauffeur, Trip.id_chauffeur == Chauffeur.id_chauffeur)\
        .all()
        
    voyages = [
        {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': f"{trip.date_depart}T{trip.heure_depart}",
            'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
            'description': f"""
                <strong>Client:</strong> {trip.client_nom}<br>
                <strong>Téléphone:</strong> {trip.client_telephone}<br>
                <strong>Chauffeur:</strong> {trip.chauffeur.nom} {trip.chauffeur.prenom}<br>
                <strong>Véhicule:</strong> {trip.vehicule.matricule} - {trip.vehicule.modele}<br>
                <strong>Passagers:</strong> {trip.nombre_passagers}<br>
                <strong>Prix:</strong> {trip.prix}€
            """.strip(),
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' else '#28a745' if trip.etat_trip == 'En cours' else '#dc3545'
        }
        for trip in trips
    ]
    return jsonify(voyages)