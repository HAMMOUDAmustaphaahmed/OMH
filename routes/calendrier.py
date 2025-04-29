from flask import Blueprint, render_template, jsonify
from models import Trip

calendrier_bp = Blueprint('calendrier', __name__, url_prefix='/calendrier')

@calendrier_bp.route('/')
def afficher_calendrier():
    # Récupérer tous les voyages depuis la base de données
    trips = Trip.query.all()
    
    # Transformer les voyages en format JSON compatible avec FullCalendar
    voyages = [
        {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': f"{trip.date_depart}T{trip.heure_depart}",
            'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
            'description': f"Client: {trip.client_nom}, Téléphone: {trip.client_telephone}, Prix: {trip.prix}€",
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' else '#28a745' if trip.etat_trip == 'En cours' else '#dc3545'
        }
        for trip in trips
    ]
    
    return render_template('calendrier.html', voyages=voyages)

@calendrier_bp.route('/api/voyages', methods=['GET'])
def api_voyages():
    trips = Trip.query.all()
    voyages = [
        {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': f"{trip.date_depart}T{trip.heure_depart}",
            'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
            'description': f"Client: {trip.client_nom}, Téléphone: {trip.client_telephone}, Prix: {trip.prix}€",
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' else '#28a745' if trip.etat_trip == 'En cours' else '#dc3545'
        }
        for trip in trips
    ]
    return jsonify(voyages)