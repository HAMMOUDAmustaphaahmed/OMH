-- Create tables
CREATE TABLE users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    telephone VARCHAR(20),
    role ENUM('admin', 'manager', 'staff') NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME,
    actif BOOLEAN DEFAULT TRUE
);

CREATE TABLE vehicules (
    id_vehicule INT AUTO_INCREMENT PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    usine VARCHAR(100) NOT NULL,
    modele VARCHAR(100) NOT NULL,
    nombre_place INT NOT NULL,
    carburant ENUM('Essence', 'Diesel', 'Hybride', 'Électrique') NOT NULL,
    kilometrage_vehicule FLOAT NOT NULL DEFAULT 0,
    couleur VARCHAR(50),
    puissance INT,
    prix_achat DECIMAL(10,2),
    etat ENUM('En marche', 'En panne', 'En entretien', 'Non disponible') NOT NULL DEFAULT 'En marche',
    annee_fabrication INT,
    date_acquisition DATE,
    assurance_expiration DATE,
    inspection_expiration DATE,
    image_url VARCHAR(255),
    notes TEXT
);

CREATE TABLE chauffeurs (
    id_chauffeur INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    numero_cin VARCHAR(20) UNIQUE NOT NULL,
    date_naissance DATE NOT NULL,
    sexe ENUM('M', 'F') NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    telephone_urgence VARCHAR(20),
    adresse TEXT NOT NULL,
    email VARCHAR(100),
    permis VARCHAR(50) NOT NULL,
    date_expiration_permis DATE NOT NULL,
    date_embauche DATE NOT NULL,
    photo_url VARCHAR(255),
    statut ENUM('Actif', 'En congé', 'Inactif') DEFAULT 'Actif',
    notes TEXT
);

CREATE TABLE trips (
    id_trip INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('Transfert', 'Transfert Société', 'Excursion', 'Événement', 'Mise à Disposition', 'Divers') NOT NULL,
    nom VARCHAR(255),
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_days JSON,
    point_depart VARCHAR(255),
    point_arrivee VARCHAR(255),
    distance FLOAT,
    heure_depart TIME,
    heure_arrivee TIME,
    date_depart DATE NOT NULL,
    date_arrivee DATE,
    nombre_jours INT,
    prix_achat DECIMAL(10,2),
    prix_vente DECIMAL(10,2),
    commission DECIMAL(10,2),
    is_commission BOOLEAN DEFAULT FALSE,
    nombre_adultes INT DEFAULT 0,
    nombre_enfants INT DEFAULT 0,
    nombre_bebes INT DEFAULT 0,
    etat_paiement ENUM('Non payé', 'Acompte', 'Payé', 'Facturé', 'Gratuit') DEFAULT 'Non payé',
    etat_trip ENUM('Planifié', 'En cours', 'Terminé', 'Annulé') DEFAULT 'Planifié',
    client_nom VARCHAR(100),
    client_telephone VARCHAR(20),
    client_email VARCHAR(100),
    commentaires TEXT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

CREATE TABLE trip_affectations (
    id_affectation INT AUTO_INCREMENT PRIMARY KEY,
    id_trip INT NOT NULL,
    id_vehicule INT NOT NULL,
    id_chauffeur INT NOT NULL,
    date_affectation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_trip) REFERENCES trips(id_trip),
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeurs(id_chauffeur)
);

CREATE TABLE trip_depenses (
    id_depense INT AUTO_INCREMENT PRIMARY KEY,
    id_trip INT NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prix_unitaire DECIMAL(10,2) NOT NULL,
    nombre_personnes INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_trip) REFERENCES trips(id_trip)
);

CREATE TABLE paiements (
    id_paiement INT AUTO_INCREMENT PRIMARY KEY,
    id_trip INT NOT NULL,
    montant_total DECIMAL(10,2) NOT NULL,
    montant_paye DECIMAL(10,2) NOT NULL,
    mode_paiement ENUM('Espèces', 'Acompte', 'Facture', 'Chèque', 'Non payé', 'Gratuit') NOT NULL,
    reference_paiement VARCHAR(100),
    banque VARCHAR(100),
    numero_cheque VARCHAR(100),
    image_cheque VARCHAR(255),
    date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP,
    recu_par INT,
    notes TEXT,
    FOREIGN KEY (id_trip) REFERENCES trips(id_trip),
    FOREIGN KEY (recu_par) REFERENCES users(id_user)
);

CREATE TABLE entretiens_vehicules (
    id_entretien INT AUTO_INCREMENT PRIMARY KEY,
    id_vehicule INT NOT NULL,
    type_entretien VARCHAR(100) NOT NULL,
    prix_entretien DECIMAL(10,2) NOT NULL,
    date_entretien DATE NOT NULL,
    kilometrage FLOAT NOT NULL,
    kilometrage_suivant FLOAT NOT NULL,
    description TEXT,
    prestataire VARCHAR(100),
    facture_reference VARCHAR(100),
    facture_url VARCHAR(255),
    pieces JSON,
    created_by INT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_vehicule INT NOT NULL,
    id_entretien INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    `read` BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (id_entretien) REFERENCES entretiens_vehicules(id_entretien)
);

CREATE TABLE depenses (
    id_depense INT AUTO_INCREMENT PRIMARY KEY,
    categorie ENUM('Carburant', 'Entretien', 'Assurance', 'Salaires', 'Taxes', 'Autre') NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    date_depense DATE NOT NULL,
    description TEXT,
    id_vehicule INT,
    created_by INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

CREATE TABLE evenements (
    id_evenement INT AUTO_INCREMENT PRIMARY KEY,
    nom_evenement VARCHAR(255) NOT NULL,
    date_debut DATETIME NOT NULL,
    date_fin DATETIME NOT NULL,
    lieu VARCHAR(255) NOT NULL,
    client_nom VARCHAR(100) NOT NULL,
    client_contact VARCHAR(100) NOT NULL,
    description TEXT,
    statut ENUM('Planifié', 'En cours', 'Terminé', 'Annulé') DEFAULT 'Planifié',
    montant_total DECIMAL(10,2),
    created_by INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

CREATE TABLE details_evenements (
    id_detail INT AUTO_INCREMENT PRIMARY KEY,
    id_evenement INT NOT NULL,
    id_vehicule INT,
    id_chauffeur INT,
    role VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (id_evenement) REFERENCES evenements(id_evenement),
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeurs(id_chauffeur)
);