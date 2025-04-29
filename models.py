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
    trips_created = db.relationship('Trip', backref='creator', lazy=True, foreign_keys='Trip.created_by')
    paiements_recu = db.relationship('Paiement', backref='receiver', lazy=True)
    entretiens_created = db.relationship('EntretienVehicule', backref='creator', lazy=True)
    depenses_created = db.relationship('Depense', backref='creator', lazy=True)
    evenements_created = db.relationship('Evenement', backref='creator', lazy=True)
    
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
    type = db.Column(db.Enum('Transfert', 'Transfert Société', 'Excursion', 'Événement', 'Mise à Disposition','Divers'), nullable=False)
    nom = db.Column(db.String(255))
    
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_days = db.Column(db.JSON)
    
    point_depart = db.Column(db.String(255))
    point_arrivee = db.Column(db.String(255))
    distance = db.Column(db.Float)
    
    heure_depart = db.Column(db.Time)
    heure_arrivee = db.Column(db.Time)
    date_depart = db.Column(db.Date, nullable=False)
    date_arrivee = db.Column(db.Date)
    nombre_jours = db.Column(db.Integer)
    
    prix_achat = db.Column(db.Numeric(10, 2))
    prix_vente = db.Column(db.Numeric(10, 2))
    commission = db.Column(db.Numeric(10, 2))
    is_commission = db.Column(db.Boolean, default=False)
    
    nombre_adultes = db.Column(db.Integer, default=0)
    nombre_enfants = db.Column(db.Integer, default=0)
    nombre_bebes = db.Column(db.Integer, default=0)
    
    etat_paiement = db.Column(db.Enum('Non payé', 'Acompte', 'Payé', 'Facturé', 'Gratuit'), default='Non payé')
    etat_trip = db.Column(db.Enum('Planifié', 'En cours', 'Terminé', 'Annulé'), default='Planifié')
    
    client_nom = db.Column(db.String(100))
    client_telephone = db.Column(db.String(20))
    client_email = db.Column(db.String(100))
    commentaires = db.Column(db.Text)
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    
    # Relations
    affectations = db.relationship('TripAffectation', backref='trip', lazy=True)
    depenses_supplementaires = db.relationship('TripDepense', backref='trip', lazy=True)
    paiements = db.relationship('Paiement', backref='trip', lazy=True)

    # Propriétés calculées
    @property
    def vehicules(self):
        return [affectation.vehicule for affectation in self.affectations]
    
    @property
    def chauffeurs(self):
        return [affectation.chauffeur for affectation in self.affectations]

class TripAffectation(db.Model):
    __tablename__ = 'trip_affectations'
    
    id_affectation = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_trip = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), nullable=False)
    id_vehicule = db.Column(db.Integer, db.ForeignKey('vehicules.id_vehicule'), nullable=False)
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeurs.id_chauffeur'), nullable=False)
    date_affectation = db.Column(db.DateTime, default=datetime.utcnow)

class TripDepense(db.Model):
    __tablename__ = 'trip_depenses'
    
    id_depense = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_trip = db.Column(db.Integer, db.ForeignKey('trips.id_trip'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prix_unitaire = db.Column(db.Numeric(10, 2), nullable=False)
    nombre_personnes = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

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