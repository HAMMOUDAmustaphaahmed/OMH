-- Création de la base de données
CREATE DATABASE IF NOT EXISTS omh_travel_db;
USE omh_travel_db;

-- Table utilisateurs
CREATE TABLE users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    telephone VARCHAR(20),
    role ENUM('admin', 'manager', 'staff') NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME,
    actif BOOLEAN DEFAULT TRUE
);

-- Table véhicules
CREATE TABLE vehicules (
    id_vehicule INT AUTO_INCREMENT PRIMARY KEY,
    matricule VARCHAR(20) NOT NULL UNIQUE,
    usine VARCHAR(100) NOT NULL,
    modele VARCHAR(100) NOT NULL,
    nombre_place INT NOT NULL,
    carburant ENUM('Essence', 'Diesel', 'Hybride', 'Électrique') NOT NULL,
    kilometrage_vehicule FLOAT NOT NULL DEFAULT 0,
    couleur VARCHAR(50),
    puissance INT,
    prix_achat DECIMAL(10, 2),
    etat ENUM('En marche', 'En panne', 'En entretien', 'Non disponible') NOT NULL DEFAULT 'En marche',
    annee_fabrication YEAR,
    date_acquisition DATE,
    assurance_expiration DATE,
    inspection_expiration DATE,
    image_url VARCHAR(255),
    notes TEXT
);

-- Table chauffeurs
CREATE TABLE chauffeurs (
    id_chauffeur INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    numero_cin VARCHAR(20) NOT NULL UNIQUE,
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

-- Table trips (voyages/trajets)
CREATE TABLE trips (
    id_trip INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('Transfert', 'Excursion', 'Location', 'Événement') NOT NULL,
    id_vehicule INT NOT NULL,
    id_chauffeur INT NOT NULL,
    point_depart VARCHAR(255) NOT NULL,
    point_arrivee VARCHAR(255) NOT NULL,
    prix DECIMAL(10, 2) NOT NULL,
    distance FLOAT,
    heure_depart TIME NOT NULL,
    heure_arrivee TIME,
    date_depart DATE NOT NULL,
    date_arrivee DATE,
    etat_paiement ENUM('Non payé', 'Acompte', 'Payé') DEFAULT 'Non payé',
    etat_trip ENUM('Planifié', 'En cours', 'Terminé', 'Annulé') DEFAULT 'Planifié',
    client_nom VARCHAR(100),
    client_telephone VARCHAR(20),
    client_email VARCHAR(100),
    nombre_passagers INT,
    commentaires TEXT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (id_chauffeur) REFERENCES chauffeurs(id_chauffeur),
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

-- Table paiements
CREATE TABLE paiements (
    id_paiement INT AUTO_INCREMENT PRIMARY KEY,
    id_trip INT NOT NULL,
    montant_total DECIMAL(10, 2) NOT NULL,
    montant_paye DECIMAL(10, 2) NOT NULL,
    reste DECIMAL(10, 2) AS (montant_total - montant_paye),
    date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP,
    mode_paiement ENUM('Espèces', 'Carte bancaire', 'Virement', 'Chèque') NOT NULL,
    reference_paiement VARCHAR(100),
    recu_par INT,
    notes TEXT,
    FOREIGN KEY (id_trip) REFERENCES trips(id_trip),
    FOREIGN KEY (recu_par) REFERENCES users(id_user)
);

-- Table entretiens véhicules
CREATE TABLE entretiens_vehicules (
    id_entretien INT AUTO_INCREMENT PRIMARY KEY,
    id_vehicule INT NOT NULL,
    type_entretien VARCHAR(100) NOT NULL,
    prix_entretien DECIMAL(10, 2) NOT NULL,
    date_entretien DATE NOT NULL,
    kilometrage FLOAT NOT NULL,
    description TEXT,
    prestataire VARCHAR(100),
    facture_reference VARCHAR(100),
    date_prochaine_maintenance DATE,
    created_by INT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

-- Table dépenses
CREATE TABLE depenses (
    id_depense INT AUTO_INCREMENT PRIMARY KEY,
    categorie ENUM('Carburant', 'Entretien', 'Assurance', 'Salaires', 'Taxes', 'Autre') NOT NULL,
    montant DECIMAL(10, 2) NOT NULL,
    date_depense DATE NOT NULL,
    description TEXT,
    id_vehicule INT,
    created_by INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_vehicule) REFERENCES vehicules(id_vehicule),
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

-- Table événements
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
    montant_total DECIMAL(10, 2),
    created_by INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id_user)
);

-- Table détails événements (pour associer plusieurs véhicules/chauffeurs à un événement)
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

-- Insertion de l'administrateur par défaut
INSERT INTO users (nom, prenom, username, password, role) 
VALUES ('Admin', 'Admin', 'admin.admin', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwlOZfxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'admin');
-- Note: le mot de passe sera haché dans le code Python
