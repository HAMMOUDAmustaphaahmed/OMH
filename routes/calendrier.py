from flask import Blueprint, render_template, jsonify
from models import Trip, Vehicule, Chauffeur, db

calendrier_bp = Blueprint('calendrier', __name__, url_prefix='/calendrier')

@calendrier_bp.route('/')
def afficher_calendrier():
    # Récupérer tous les voyages avec les relations chauffeur et véhicule
    trips = db.session.query(Trip).all()
    
    # Transformer les voyages en format JSON compatible avec FullCalendar
    voyages = []
    for trip in trips:
        # Récupérer tous les véhicules et chauffeurs pour ce voyage
        vehicules = []
        chauffeurs = []
        for affectation in trip.affectations:
            vehicules.append(f"{affectation.vehicule.matricule} - {affectation.vehicule.modele}")
            chauffeurs.append(f"{affectation.chauffeur.nom} {affectation.chauffeur.prenom}")
        
        voyage = {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': f"{trip.date_depart}T{trip.heure_depart}",
            'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
            'description': f"""
                <strong>Client:</strong> {trip.client_nom}<br>
                <strong>Téléphone:</strong> {trip.client_telephone}<br>
                <strong>Chauffeurs:</strong> {' | '.join(chauffeurs)}<br>
                <strong>Véhicules:</strong> {' | '.join(vehicules)}<br>
                <strong>Passagers:</strong> {trip.nombre_adultes + trip.nombre_enfants + trip.nombre_bebes}<br>
                <strong>Prix:</strong> {trip.prix_vente}€
            """.strip(),
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' else '#28a745' if trip.etat_trip == 'En cours' else '#dc3545'
        }
        voyages.append(voyage)
    
    return render_template('calendrier.html', voyages=voyages)

@calendrier_bp.route('/api/voyages', methods=['GET'])
def api_voyages():
    trips = db.session.query(Trip).all()
    
    voyages = []
    for trip in trips:
        # Récupérer tous les véhicules et chauffeurs pour ce voyage
        vehicules = []
        chauffeurs = []
        for affectation in trip.affectations:
            vehicules.append(f"{affectation.vehicule.matricule} - {affectation.vehicule.modele}")
            chauffeurs.append(f"{affectation.chauffeur.nom} {affectation.chauffeur.prenom}")
            
        voyage = {
            'id': trip.id_trip,
            'title': f"{trip.type} - {trip.point_depart} -> {trip.point_arrivee}",
            'start': f"{trip.date_depart}T{trip.heure_depart}",
            'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
            'description': f"""
                <strong>Client:</strong> {trip.client_nom}<br>
                <strong>Téléphone:</strong> {trip.client_telephone}<br>
                <strong>Chauffeurs:</strong> {' | '.join(chauffeurs)}<br>
                <strong>Véhicules:</strong> {' | '.join(vehicules)}<br>
                <strong>Passagers:</strong> {trip.nombre_adultes + trip.nombre_enfants + trip.nombre_bebes}<br>
                <strong>Prix:</strong> {trip.prix_vente}€
            """.strip(),
            'backgroundColor': '#007bff' if trip.etat_trip == 'Planifié' else '#28a745' if trip.etat_trip == 'En cours' else '#dc3545'
        }
        voyages.append(voyage)
        
    return jsonify(voyages)

def get_status_color(status):
    colors = {
        'Planifié': '#3498db',    # Bleu
        'En cours': '#f1c40f',    # Jaune
        'Terminé': '#2ecc71',     # Vert
        'Annulé': '#e74c3c'       # Rouge
    }
    return colors.get(status, '#95a5a6')  # Gris par défaut