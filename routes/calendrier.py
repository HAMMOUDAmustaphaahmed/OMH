from flask import Blueprint, render_template, jsonify
from models import Trip, Vehicule, Chauffeur, TripAffectation, db

calendrier_bp = Blueprint('calendrier', __name__, url_prefix='/calendrier')

@calendrier_bp.route('/')
def afficher_calendrier():
    # Récupérer tous les voyages avec leurs affectations
    trips = db.session.query(Trip)\
        .join(TripAffectation)\
        .join(Vehicule, TripAffectation.id_vehicule == Vehicule.id_vehicule)\
        .join(Chauffeur, TripAffectation.id_chauffeur == Chauffeur.id_chauffeur)\
        .all()
    
    # Transformer les voyages en format JSON compatible avec FullCalendar
    voyages = []
    for trip in trips:
        # Obtenir le premier véhicule et chauffeur affectés (s'il y en a)
        affectation = trip.affectations[0] if trip.affectations else None
        if affectation:
            vehicule = affectation.vehicule
            chauffeur = affectation.chauffeur
            
            # Calculer le nombre total de passagers
            total_passagers = (trip.nombre_adultes or 0) + (trip.nombre_enfants or 0) + (trip.nombre_bebes or 0)
            
            # Formater les prix avec gestion des None
            prix_vente = f"{float(trip.prix_vente):.2f}" if trip.prix_vente else "N/A"
            
            voyage = {
                'id': trip.id_trip,
                'title': f"{trip.type} - {trip.point_depart} → {trip.point_arrivee}",
                'start': f"{trip.date_depart}T{trip.heure_depart}" if trip.heure_depart else f"{trip.date_depart}",
                'end': f"{trip.date_arrivee}T{trip.heure_arrivee}" if trip.date_arrivee and trip.heure_arrivee else None,
                'description': f"""
                    <div class="event-details">
                        <h4>{trip.nom or trip.type}</h4>
                        <p><i class="fas fa-user"></i> <strong>Client:</strong> {trip.client_nom or 'Non spécifié'}</p>
                        <p><i class="fas fa-phone"></i> <strong>Tél:</strong> {trip.client_telephone or 'Non spécifié'}</p>
                        <p><i class="fas fa-id-card"></i> <strong>Chauffeur:</strong> {chauffeur.nom} {chauffeur.prenom}</p>
                        <p><i class="fas fa-car"></i> <strong>Véhicule:</strong> {vehicule.modele} ({vehicule.matricule})</p>
                        <p><i class="fas fa-users"></i> <strong>Passagers:</strong> {total_passagers}</p>
                        <p><i class="fas fa-money-bill"></i> <strong>Prix:</strong> {prix_vente} TND</p>
                        <p><i class="fas fa-circle"></i> <strong>État:</strong> {trip.etat_trip}</p>
                    </div>
                """.strip(),
                'backgroundColor': get_status_color(trip.etat_trip),
                'borderColor': get_status_color(trip.etat_trip),
                'textColor': '#ffffff',
                'className': f'trip-status-{trip.etat_trip.lower()}',
                'url': f'/trips/{trip.id_trip}'
            }
            voyages.append(voyage)
    
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
def get_status_color(status):
    colors = {
        'Planifié': '#3498db',    # Bleu
        'En cours': '#f1c40f',    # Jaune
        'Terminé': '#2ecc71',     # Vert
        'Annulé': '#e74c3c'       # Rouge
    }
    return colors.get(status, '#95a5a6')  # Gris par défaut