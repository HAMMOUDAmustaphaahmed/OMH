from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    role = db.Column(db.Enum('admin', 'manager', 'staff'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    actif = db.Column(db.Boolean, default=True)

    # Relations
    trips_created = db.relationship('Trip', backref='creator', lazy=True, foreign_keys='Trip.created_by_id')
    paiements_recu = db.relationship('Paiement', backref='receiver', lazy=True, foreign_keys='Paiement.recu_par')
    entretiens_created = db.relationship('EntretienVehicule', backref='creator', lazy=True, foreign_keys='EntretienVehicule.created_by')
    depenses_created = db.relationship('Depense', backref='creator', lazy=True, foreign_keys='Depense.created_by')
    evenements_created = db.relationship('Evenement', backref='creator', lazy=True, foreign_keys='Evenement.created_by')

    def get_id(self):
        return str(self.id_user)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_roles(self):
        return [role.strip() for role in self.role.split(',') if role.strip()]

    def has_role(self, role):
        return role in self.get_roles()

    def has_any_role(self, roles):
        user_roles = self.get_roles()
        return any(role in user_roles for role in roles)

    def add_role(self, new_role):
        current_roles = self.get_roles()
        if new_role not in current_roles:
            current_roles.append(new_role)
            self.role = ','.join(current_roles)

    def remove_role(self, role_to_remove):
        current_roles = self.get_roles()
        if role_to_remove in current_roles:
            current_roles.remove(role_to_remove)
            self.role = ','.join(current_roles)

    @classmethod
    def create_user(cls, nom, prenom, role, password=None):
        username = f"{nom.lower()}.{prenom.lower()}"
        if password is None:
            password = f"{nom.lower()}.{prenom.lower()}"
        user = cls(
            nom=nom,
            prenom=prenom,
            username=username,
            role=role
        )
        user.set_password(password)
        return user

class Vehicule(db.Model):
    __tablename__ = 'vehicules'
    id_vehicule = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    usine = db.Column(db.String(100), nullable=False)
    modele = db.Column(db.String(100), nullable=False)
    nombre_place = db.Column(db.Integer, nullable=False)
    carburant = db.Column(db.Enum('Essence', 'Diesel', 'Hybride', 'Électrique'), nullable=False)
    kilometrage_vehicule = db.Column(db.Float, nullable=False, default=0)
    couleur = db.Column(db.String(50))
    puissance = db.Column(db.Integer)
    prix_achat = db.Column(db.Numeric(10, 2))
    etat = db.Column(db.Enum('En marche', 'En panne', 'En entretien', 'Non disponible'), nullable=False, default='En marche')
    annee_fabrication = db.Column(db.Integer)
    date_acquisition = db.Column(db.Date)
    assurance_expiration = db.Column(db.Date)
    inspection_expiration = db.Column(db.Date)
    image_url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    type_vehicule = db.Column(db.Enum('OMH', 'Grand Taxi Touristique', 'Autres'), nullable=False, default='OMH')

    # Relations
    affectations = db.relationship('TripAffectation', backref='vehicule', lazy=True)
    entretiens = db.relationship('EntretienVehicule', backref='vehicule', lazy=True)
    depenses = db.relationship('Depense', backref='vehicule', lazy=True)
    details_evenements = db.relationship('DetailEvenement', backref='vehicule', lazy=True)
    notifications = db.relationship('Notification', backref='vehicule', lazy=True)

class Chauffeur(db.Model):
    __tablename__ = 'chauffeurs'
    id_chauffeur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    numero_cin = db.Column(db.String(20), unique=True, nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    sexe = db.Column(db.Enum('M', 'F'), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    telephone_urgence = db.Column(db.String(20))
    adresse = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100))
    permis = db.Column(db.String(50), nullable=False)
    date_expiration_permis = db.Column(db.Date, nullable=False)
    date_embauche = db.Column(db.Date, nullable=False)
    photo_url = db.Column(db.String(255))
    statut = db.Column(db.Enum('Actif', 'En congé', 'Inactif'), default='Actif')
    notes = db.Column(db.Text)

    # Relations
    affectations = db.relationship('TripAffectation', backref='chauffeur', lazy=True)
    details_evenements = db.relationship('DetailEvenement', backref='chauffeur', lazy=True)

class Trip(db.Model):
    __tablename__ = 'trips'
    id_trip = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_voyage = db.Column(db.String(100), unique=True, nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum('Excursion', 'Transfert', 'Divers', 'Varié', 'Commission Vente'), nullable=False)

    # Client info
    client_nom = db.Column(db.String(100), nullable=False)
    client_telephone = db.Column(db.String(20))
    client_email = db.Column(db.String(100))

    # Dates
    date_depart = db.Column(db.DateTime, nullable=False)
    date_retour = db.Column(db.DateTime)

    # Passagers
    total_passagers = db.Column(db.Integer, nullable=False)
    nombre_adultes = db.Column(db.Integer, default=0)
    nombre_enfants = db.Column(db.Integer, default=0)
    nombre_bebes = db.Column(db.Integer, default=0)

    # Prix
    tarif = db.Column(db.Numeric(10, 2), nullable=False)
    commission_achat = db.Column(db.Boolean, default=False)
    montant_commission = db.Column(db.Numeric(10, 2))

    # Itinéraire
    point_depart = db.Column(db.String(255), nullable=False)
    point_arrivee = db.Column(db.String(255), nullable=False)
    points_intermediaires = db.Column(db.JSON)
    retour_vide = db.Column(db.Boolean)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id_user'))

    # Relations
    vehicules = db.relationship('Vehicule', secondary='trip_vehicules', backref='trips')
    chauffeurs = db.relationship('Chauffeur', secondary='trip_chauffeurs', backref='trips')
    depenses = db.relationship('TripDepense', backref='trip', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Trip, self).__init__(**kwargs)
        if not self.code_voyage:  # Changez 'code' en 'code_voyage'
            self.generate_trip_code()

    def generate_trip_code(self):
        try:
            current_year = datetime.utcnow().year % 100
            last_trip = Trip.query.filter(
                Trip.code_voyage.like(f'{current_year}-%')  # Changez 'code' en 'code_voyage'
            ).order_by(Trip.code_voyage.desc()).first()  # Changez 'code' en 'code_voyage'
            
            if last_trip:
                last_number = int(last_trip.code_voyage.split('-')[1])  # Changez 'code' en 'code_voyage'
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.code_voyage = f"{current_year}-{new_number}"  # Changez 'code' en 'code_voyage'
        except Exception as e:
            # En cas d'erreur, générer un code basé sur le timestamp
            self.code_voyage = f"{datetime.now().strftime('%y-%m%d%H%M')}"

# Table de liaison pour les véhicules
class TripVehicule(db.Model):
    __tablename__ = 'trip_vehicules'
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), primary_key=True)
    vehicule_id = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'), primary_key=True)

# Table de liaison pour les chauffeurs
class TripChauffeur(db.Model):
    __tablename__ = 'trip_chauffeurs'
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), primary_key=True)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('chauffeurs.id_chauffeur'), primary_key=True)

class TripDepense(db.Model):
    __tablename__ = 'trip_depenses'
    id_depense = db.Column(db.Integer, primary_key=True)
    id_trip = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), nullable=False)  # Changé de trip_id à id_trip
    nom = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    

class VenteTrip(db.Model):
    __tablename__ = 'ventes_trips'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    client_nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id_user'))

class Paiement(db.Model):
    __tablename__ = 'paiements'
    id_paiement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_trip = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), nullable=False)
    montant_total = db.Column(db.Numeric(10, 2), nullable=False)
    montant_paye = db.Column(db.Numeric(10, 2), nullable=False)
    mode_paiement = db.Column(db.Enum('Espèces', 'Acompte', 'Facture', 'Chèque', 'Non payé', 'Gratuit'), nullable=False)
    reference_paiement = db.Column(db.String(100))
    banque = db.Column(db.String(100))
    numero_cheque = db.Column(db.String(100))
    image_cheque = db.Column(db.String(255))
    date_paiement = db.Column(db.DateTime, default=datetime.utcnow)
    recu_par = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    notes = db.Column(db.Text)

class EntretienVehicule(db.Model):
    __tablename__ = 'entretiens_vehicules'
    id_entretien = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'), nullable=False)
    type_entretien = db.Column(db.String(100), nullable=False)
    prix_entretien = db.Column(db.Numeric(10, 2), nullable=False)
    date_entretien = db.Column(db.Date, nullable=False)
    kilometrage = db.Column(db.Float, nullable=False)
    kilometrage_suivant = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    prestataire = db.Column(db.String(100))
    facture_reference = db.Column(db.String(100))
    facture_url = db.Column(db.String(255))
    pieces = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    notifications = db.relationship('Notification', backref='entretien', lazy=True)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'), nullable=False)
    id_entretien = db.Column(db.Integer, db.ForeignKey('entretiens_vehicules.id_entretien'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

class Depense(db.Model):
    __tablename__ = 'depenses'
    id_depense = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categorie = db.Column(db.Enum('Carburant', 'Entretien', 'Assurance', 'Salaires', 'Taxes', 'Autre'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_depense = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Evenement(db.Model):
    __tablename__ = 'evenements'
    id_evenement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_evenement = db.Column(db.String(255), nullable=False)
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    lieu = db.Column(db.String(255), nullable=False)
    client_nom = db.Column(db.String(100), nullable=False)
    client_contact = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    statut = db.Column(db.Enum('Planifié', 'En cours', 'Terminé', 'Annulé'), default='Planifié')
    montant_total = db.Column(db.Numeric(10, 2))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.relationship('DetailEvenement', backref='evenement', lazy=True)

class DetailEvenement(db.Model):
    __tablename__ = 'details_evenements'
    id_detail = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_evenement = db.Column(db.Integer, db.ForeignKey('evenements.id_evenement'), nullable=False)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'))
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeurs.id_chauffeur'))
    role = db.Column(db.String(100))
    notes = db.Column(db.Text)

# Table de liaison voyage-véhicule-chauffeur si besoin (si tu utilises TripAffectation dans tes autres modèles)
class TripAffectation(db.Model):
    __tablename__ = 'trip_affectations'
    id_affectation = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_trip = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), nullable=False)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'), nullable=False)
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeurs.id_chauffeur'), nullable=False)
    date_affectation = db.Column(db.DateTime, default=datetime.utcnow)


# Ajout/Modification dans models.py

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id_transaction = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum('Revenu', 'Dépense', 'Transfert'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_transaction = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(100), nullable=False)
    sous_categorie = db.Column(db.String(100))
    mode_paiement = db.Column(db.String(50))
    reference = db.Column(db.String(100))
    statut = db.Column(db.Enum('Complété', 'En attente', 'Annulé'), default='Complété')
    
    # Relations
    id_compte = db.Column(db.Integer, db.ForeignKey('comptes_bancaires.id_compte'))
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'))
    id_trip = db.Column(db.Integer, db.ForeignKey('trips.id_trip'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    
    pieces_jointes = db.relationship('PieceJointe', backref='transaction', lazy=True)
    
    @property
    def montant_formate(self):
        return "{:,.2f} DT".format(float(self.montant))

class CompteBancaire(db.Model):
    __tablename__ = 'comptes_bancaires'
    
    id_compte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_banque = db.Column(db.String(100), nullable=False)
    numero_compte = db.Column(db.String(50), nullable=False, unique=True)
    type_compte = db.Column(db.String(50))
    solde_actuel = db.Column(db.Numeric(10, 2), default=0)
    devise = db.Column(db.String(3), default='TND')
    date_ouverture = db.Column(db.Date)
    statut = db.Column(db.Enum('Actif', 'Inactif'), default='Actif')
    
    transactions = db.relationship('Transaction', backref='compte', lazy=True)

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id_budget = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categorie = db.Column(db.String(100), nullable=False)
    montant_prevu = db.Column(db.Numeric(10, 2), nullable=False)
    montant_actuel = db.Column(db.Numeric(10, 2), default=0)
    periode_debut = db.Column(db.Date, nullable=False)
    periode_fin = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    @property
    def pourcentage_utilisation(self):
        if float(self.montant_prevu) == 0:
            return 0
        return (float(self.montant_actuel) / float(self.montant_prevu)) * 100

class PieceJointe(db.Model):
    __tablename__ = 'pieces_jointes'
    
    id_piece = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_transaction = db.Column(db.Integer, db.ForeignKey('transactions.id_transaction'))
    type_document = db.Column(db.String(50))
    nom_fichier = db.Column(db.String(255))
    url_fichier = db.Column(db.String(500))
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)

class RapportFinancier(db.Model):
    __tablename__ = 'rapports_financiers'
    
    id_rapport = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_rapport = db.Column(db.String(100), nullable=False)
    periode_debut = db.Column(db.Date, nullable=False)
    periode_fin = db.Column(db.Date, nullable=False)
    contenu = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def periode_formatee(self):
        return f"{self.periode_debut.strftime('%d/%m/%Y')} - {self.periode_fin.strftime('%d/%m/%Y')}"

class DepenseFinance(db.Model):  # Changement du nom de la classe
    __tablename__ = 'depenses_finance'  # Changement du nom de la table
    
    id_depense = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categorie = db.Column(db.Enum(
        'Carburant', 'Entretien', 'Assurance', 'Salaires', 
        'Taxes', 'Fournitures', 'Marketing', 'Location',
        'Utilities', 'Télécommunications', 'Formation',
        'Autre'
    ), nullable=False)
    sous_categorie = db.Column(db.String(100))
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_depense = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    justificatif_url = db.Column(db.String(500))
    mode_paiement = db.Column(db.String(50))
    reference_paiement = db.Column(db.String(100))
    statut = db.Column(db.Enum('Payé', 'En attente', 'Annulé'), default='Payé')
    recurrent = db.Column(db.Boolean, default=False)
    frequence = db.Column(db.String(50))
    
    # Relations
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'))
    id_compte = db.Column(db.Integer, db.ForeignKey('comptes_bancaires.id_compte'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations avec d'autres tables
    vehicule = db.relationship('Vehicule', backref='depenses_finance')
    compte = db.relationship('CompteBancaire', backref='depenses_finance')
    user = db.relationship('User', backref='depenses_finance')

    @property
    def montant_formate(self):
        return "{:,.2f} DT".format(float(self.montant))
    __tablename__ = 'depenses_finance'
    
    id_depense = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categorie = db.Column(db.Enum(
        'Carburant', 'Entretien', 'Assurance', 'Salaires', 
        'Taxes', 'Fournitures', 'Marketing', 'Location',
        'Utilities', 'Télécommunications', 'Formation',
        'Autre'
    ), nullable=False)
    sous_categorie = db.Column(db.String(100))
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_depense = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    justificatif_url = db.Column(db.String(500))
    mode_paiement = db.Column(db.String(50))
    reference_paiement = db.Column(db.String(100))
    statut = db.Column(db.Enum('Payé', 'En attente', 'Annulé'), default='Payé')
    recurrent = db.Column(db.Boolean, default=False)
    frequence = db.Column(db.String(50))
    
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'))
    id_compte = db.Column(db.Integer, db.ForeignKey('comptes_bancaires.id_compte'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def montant_formate(self):
        return "{:,.2f} DT".format(float(self.montant))