-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
<<<<<<< HEAD
-- Généré le : mar. 29 avr. 2025 à 07:21
=======
-- Généré le : mer. 23 avr. 2025 à 18:17
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `omh_travel_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `chauffeurs`
--

CREATE TABLE `chauffeurs` (
  `id_chauffeur` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `numero_cin` varchar(20) NOT NULL,
  `date_naissance` date NOT NULL,
  `sexe` enum('M','F') NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `telephone_urgence` varchar(20) DEFAULT NULL,
  `adresse` text NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `permis` varchar(50) NOT NULL,
  `date_expiration_permis` date NOT NULL,
  `date_embauche` date NOT NULL,
  `photo_url` varchar(255) DEFAULT NULL,
  `statut` enum('Actif','En congé','Inactif') DEFAULT 'Actif',
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

<<<<<<< HEAD
--
-- Déchargement des données de la table `chauffeurs`
--

INSERT INTO `chauffeurs` (`id_chauffeur`, `nom`, `prenom`, `numero_cin`, `date_naissance`, `sexe`, `telephone`, `telephone_urgence`, `adresse`, `email`, `permis`, `date_expiration_permis`, `date_embauche`, `photo_url`, `statut`, `notes`) VALUES
(1, 'fleni', 'foulan', '12345678', '1990-01-01', 'M', '12345678', '12345678', 'cdscsdcsdc', 'driver1@gmail.com', '12345678', '1990-01-01', '1990-01-01', NULL, 'Actif', 'sfdvsv');

=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- --------------------------------------------------------

--
-- Structure de la table `depenses`
--

CREATE TABLE `depenses` (
  `id_depense` int(11) NOT NULL,
  `categorie` enum('Carburant','Entretien','Assurance','Salaires','Taxes','Autre') NOT NULL,
  `montant` decimal(10,2) NOT NULL,
  `date_depense` date NOT NULL,
  `description` text DEFAULT NULL,
  `id_vehicule` int(11) DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `details_evenements`
--

CREATE TABLE `details_evenements` (
  `id_detail` int(11) NOT NULL,
  `id_evenement` int(11) NOT NULL,
  `id_vehicule` int(11) DEFAULT NULL,
  `id_chauffeur` int(11) DEFAULT NULL,
  `role` varchar(100) DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `entretiens_vehicules`
--

CREATE TABLE `entretiens_vehicules` (
  `id_entretien` int(11) NOT NULL,
  `id_vehicule` int(11) NOT NULL,
  `type_entretien` varchar(100) NOT NULL,
  `prix_entretien` decimal(10,2) NOT NULL,
  `date_entretien` date NOT NULL,
  `kilometrage` float NOT NULL,
<<<<<<< HEAD
  `kilometrage_suivant` float DEFAULT NULL,
  `description` text DEFAULT NULL,
  `prestataire` varchar(100) DEFAULT NULL,
  `facture_reference` varchar(100) DEFAULT NULL,
  `facture_url` varchar(255) DEFAULT NULL,
  `pieces` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`pieces`)),
=======
  `description` text DEFAULT NULL,
  `prestataire` varchar(100) DEFAULT NULL,
  `facture_reference` varchar(100) DEFAULT NULL,
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
  `date_prochaine_maintenance` date DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

<<<<<<< HEAD
--
-- Déchargement des données de la table `entretiens_vehicules`
--

INSERT INTO `entretiens_vehicules` (`id_entretien`, `id_vehicule`, `type_entretien`, `prix_entretien`, `date_entretien`, `kilometrage`, `kilometrage_suivant`, `description`, `prestataire`, `facture_reference`, `facture_url`, `pieces`, `date_prochaine_maintenance`, `created_by`, `date_creation`) VALUES
(1, 1, 'Vidange', 48498.00, '1990-01-01', 156555, 110500, 'sdcsdcsdc', 'sdcsd', '4897489', NULL, '[\"sdcsdc\", \"sdcsdcsdcsdc\"]', NULL, 1, '2025-04-28 20:50:30');

=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- --------------------------------------------------------

--
-- Structure de la table `evenements`
--

CREATE TABLE `evenements` (
  `id_evenement` int(11) NOT NULL,
  `nom_evenement` varchar(255) NOT NULL,
  `date_debut` datetime NOT NULL,
  `date_fin` datetime NOT NULL,
  `lieu` varchar(255) NOT NULL,
  `client_nom` varchar(100) NOT NULL,
  `client_contact` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `statut` enum('Planifié','En cours','Terminé','Annulé') DEFAULT 'Planifié',
  `montant_total` decimal(10,2) DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
<<<<<<< HEAD
-- Structure de la table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `id_vehicule` int(11) NOT NULL,
  `id_entretien` int(11) NOT NULL,
  `message` varchar(255) NOT NULL,
  `severity` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `read` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `notifications`
--

INSERT INTO `notifications` (`id`, `id_vehicule`, `id_entretien`, `message`, `severity`, `created_at`, `read`) VALUES
(1, 1, 1, 'Entretien à prévoir pour 211TN1010 dans moins de 1000 km', 'yellow', '2025-04-28 20:53:29', 1),
(2, 1, 1, 'URGENT: Entretien nécessaire pour 211TN1010 dans moins de 500 km', 'red', '2025-04-28 20:56:48', 1),
(3, 1, 1, 'URGENT: Entretien nécessaire pour 211TN1010 dans moins de 500 km', 'red', '2025-04-28 20:57:11', 0),
(4, 1, 1, 'Entretien à prévoir pour 211TN1010 dans moins de 1000 km', 'yellow', '2025-04-28 20:57:25', 0);

-- --------------------------------------------------------

--
=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- Structure de la table `paiements`
--

CREATE TABLE `paiements` (
  `id_paiement` int(11) NOT NULL,
  `id_trip` int(11) NOT NULL,
  `montant_total` decimal(10,2) NOT NULL,
  `montant_paye` decimal(10,2) NOT NULL,
  `reste` decimal(10,2) GENERATED ALWAYS AS (`montant_total` - `montant_paye`) VIRTUAL,
  `date_paiement` datetime DEFAULT current_timestamp(),
  `mode_paiement` enum('Espèces','Carte bancaire','Virement','Chèque') NOT NULL,
  `reference_paiement` varchar(100) DEFAULT NULL,
  `recu_par` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `trips`
--

CREATE TABLE `trips` (
  `id_trip` int(11) NOT NULL,
  `type` enum('Transfert','Excursion','Location','Événement') NOT NULL,
  `id_vehicule` int(11) NOT NULL,
  `id_chauffeur` int(11) NOT NULL,
  `point_depart` varchar(255) NOT NULL,
  `point_arrivee` varchar(255) NOT NULL,
  `prix` decimal(10,2) NOT NULL,
  `distance` float DEFAULT NULL,
  `heure_depart` time NOT NULL,
  `heure_arrivee` time DEFAULT NULL,
  `date_depart` date NOT NULL,
  `date_arrivee` date DEFAULT NULL,
  `etat_paiement` enum('Non payé','Acompte','Payé') DEFAULT 'Non payé',
  `etat_trip` enum('Planifié','En cours','Terminé','Annulé') DEFAULT 'Planifié',
  `client_nom` varchar(100) DEFAULT NULL,
  `client_telephone` varchar(20) DEFAULT NULL,
  `client_email` varchar(100) DEFAULT NULL,
  `nombre_passagers` int(11) DEFAULT NULL,
  `commentaires` text DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `created_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

<<<<<<< HEAD
--
-- Déchargement des données de la table `trips`
--

INSERT INTO `trips` (`id_trip`, `type`, `id_vehicule`, `id_chauffeur`, `point_depart`, `point_arrivee`, `prix`, `distance`, `heure_depart`, `heure_arrivee`, `date_depart`, `date_arrivee`, `etat_paiement`, `etat_trip`, `client_nom`, `client_telephone`, `client_email`, `nombre_passagers`, `commentaires`, `date_creation`, `created_by`) VALUES
(1, 'Transfert', 1, 1, 'Sousse', 'Monastir', 50.00, 15, '20:00:00', '21:00:00', '2025-04-28', '2025-04-28', 'Payé', 'Planifié', 'X', '12345678', 'client@gmail.com', 4, 'sdsdscre', '2025-04-28 10:30:17', 1);

=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id_user` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `role` enum('admin','manager','staff') NOT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `derniere_connexion` datetime DEFAULT NULL,
  `actif` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id_user`, `nom`, `prenom`, `username`, `password`, `email`, `telephone`, `role`, `date_creation`, `derniere_connexion`, `actif`) VALUES
<<<<<<< HEAD
(1, 'Admin', 'Admin', 'admin.admin', 'pbkdf2:sha256:260000$4Jek92C0RqfSmAGu$0c1335488b7f7d1f1bbce006be5fd6071e418d06056376ad83b8747e13d08193', 'admin@gmail.com', '12345678', 'admin', '2025-04-23 09:33:02', '2025-04-28 17:03:52', 1);
=======
(1, 'Admin', 'Admin', 'admin.admin', 'admin.admin', 'admin@gmail.com', '12345678', 'admin', '2025-04-23 09:33:02', '2025-04-23 10:18:40', 1);
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4

-- --------------------------------------------------------

--
-- Structure de la table `vehicules`
--

CREATE TABLE `vehicules` (
  `id_vehicule` int(11) NOT NULL,
  `matricule` varchar(20) NOT NULL,
  `usine` varchar(100) NOT NULL,
  `modele` varchar(100) NOT NULL,
  `nombre_place` int(11) NOT NULL,
  `carburant` enum('Essence','Diesel','Hybride','Électrique') NOT NULL,
  `kilometrage_vehicule` float NOT NULL DEFAULT 0,
  `couleur` varchar(50) DEFAULT NULL,
  `puissance` int(11) DEFAULT NULL,
  `prix_achat` decimal(10,2) DEFAULT NULL,
  `etat` enum('En marche','En panne','En entretien','Non disponible') NOT NULL DEFAULT 'En marche',
  `annee_fabrication` year(4) DEFAULT NULL,
  `date_acquisition` date DEFAULT NULL,
  `assurance_expiration` date DEFAULT NULL,
  `inspection_expiration` date DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `vehicules`
--

INSERT INTO `vehicules` (`id_vehicule`, `matricule`, `usine`, `modele`, `nombre_place`, `carburant`, `kilometrage_vehicule`, `couleur`, `puissance`, `prix_achat`, `etat`, `annee_fabrication`, `date_acquisition`, `assurance_expiration`, `inspection_expiration`, `image_url`, `notes`) VALUES
<<<<<<< HEAD
(1, '211TN1010', 'Peugeot', '205', 5, 'Essence', 110152, 'rouge', 5, NULL, 'En marche', NULL, '1990-01-01', '1990-01-01', '1990-01-01', NULL, 'None'),
(2, '122TN4456', 'Toyota', 'Corolla', 5, 'Diesel', 123456, NULL, NULL, NULL, 'En marche', NULL, NULL, NULL, NULL, NULL, NULL);
=======
(1, '211TN1010', 'Peugeot', '205', 5, 'Essence', 110152, NULL, NULL, NULL, 'En marche', NULL, NULL, NULL, NULL, NULL, NULL);
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `chauffeurs`
--
ALTER TABLE `chauffeurs`
  ADD PRIMARY KEY (`id_chauffeur`),
  ADD UNIQUE KEY `numero_cin` (`numero_cin`);

--
-- Index pour la table `depenses`
--
ALTER TABLE `depenses`
  ADD PRIMARY KEY (`id_depense`),
  ADD KEY `id_vehicule` (`id_vehicule`),
  ADD KEY `created_by` (`created_by`);

--
-- Index pour la table `details_evenements`
--
ALTER TABLE `details_evenements`
  ADD PRIMARY KEY (`id_detail`),
  ADD KEY `id_evenement` (`id_evenement`),
  ADD KEY `id_vehicule` (`id_vehicule`),
  ADD KEY `id_chauffeur` (`id_chauffeur`);

--
-- Index pour la table `entretiens_vehicules`
--
ALTER TABLE `entretiens_vehicules`
  ADD PRIMARY KEY (`id_entretien`),
  ADD KEY `id_vehicule` (`id_vehicule`),
  ADD KEY `created_by` (`created_by`);

--
-- Index pour la table `evenements`
--
ALTER TABLE `evenements`
  ADD PRIMARY KEY (`id_evenement`),
  ADD KEY `created_by` (`created_by`);

--
<<<<<<< HEAD
-- Index pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_vehicule` (`id_vehicule`),
  ADD KEY `id_entretien` (`id_entretien`);

--
=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- Index pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD PRIMARY KEY (`id_paiement`),
  ADD KEY `id_trip` (`id_trip`),
  ADD KEY `recu_par` (`recu_par`);

--
-- Index pour la table `trips`
--
ALTER TABLE `trips`
  ADD PRIMARY KEY (`id_trip`),
  ADD KEY `id_vehicule` (`id_vehicule`),
  ADD KEY `id_chauffeur` (`id_chauffeur`),
  ADD KEY `created_by` (`created_by`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Index pour la table `vehicules`
--
ALTER TABLE `vehicules`
  ADD PRIMARY KEY (`id_vehicule`),
  ADD UNIQUE KEY `matricule` (`matricule`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `chauffeurs`
--
ALTER TABLE `chauffeurs`
<<<<<<< HEAD
  MODIFY `id_chauffeur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
=======
  MODIFY `id_chauffeur` int(11) NOT NULL AUTO_INCREMENT;
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4

--
-- AUTO_INCREMENT pour la table `depenses`
--
ALTER TABLE `depenses`
  MODIFY `id_depense` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `details_evenements`
--
ALTER TABLE `details_evenements`
  MODIFY `id_detail` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `entretiens_vehicules`
--
ALTER TABLE `entretiens_vehicules`
<<<<<<< HEAD
  MODIFY `id_entretien` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
=======
  MODIFY `id_entretien` int(11) NOT NULL AUTO_INCREMENT;
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4

--
-- AUTO_INCREMENT pour la table `evenements`
--
ALTER TABLE `evenements`
  MODIFY `id_evenement` int(11) NOT NULL AUTO_INCREMENT;

--
<<<<<<< HEAD
-- AUTO_INCREMENT pour la table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- AUTO_INCREMENT pour la table `paiements`
--
ALTER TABLE `paiements`
  MODIFY `id_paiement` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `trips`
--
ALTER TABLE `trips`
<<<<<<< HEAD
  MODIFY `id_trip` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
=======
  MODIFY `id_trip` int(11) NOT NULL AUTO_INCREMENT;
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `vehicules`
--
ALTER TABLE `vehicules`
<<<<<<< HEAD
  MODIFY `id_vehicule` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
=======
  MODIFY `id_vehicule` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `depenses`
--
ALTER TABLE `depenses`
  ADD CONSTRAINT `depenses_ibfk_1` FOREIGN KEY (`id_vehicule`) REFERENCES `vehicules` (`id_vehicule`),
  ADD CONSTRAINT `depenses_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id_user`);

--
-- Contraintes pour la table `details_evenements`
--
ALTER TABLE `details_evenements`
  ADD CONSTRAINT `details_evenements_ibfk_1` FOREIGN KEY (`id_evenement`) REFERENCES `evenements` (`id_evenement`),
  ADD CONSTRAINT `details_evenements_ibfk_2` FOREIGN KEY (`id_vehicule`) REFERENCES `vehicules` (`id_vehicule`),
  ADD CONSTRAINT `details_evenements_ibfk_3` FOREIGN KEY (`id_chauffeur`) REFERENCES `chauffeurs` (`id_chauffeur`);

--
-- Contraintes pour la table `entretiens_vehicules`
--
ALTER TABLE `entretiens_vehicules`
  ADD CONSTRAINT `entretiens_vehicules_ibfk_1` FOREIGN KEY (`id_vehicule`) REFERENCES `vehicules` (`id_vehicule`),
  ADD CONSTRAINT `entretiens_vehicules_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id_user`);

--
-- Contraintes pour la table `evenements`
--
ALTER TABLE `evenements`
  ADD CONSTRAINT `evenements_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id_user`);

--
<<<<<<< HEAD
-- Contraintes pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`id_vehicule`) REFERENCES `vehicules` (`id_vehicule`),
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`id_entretien`) REFERENCES `entretiens_vehicules` (`id_entretien`);

--
=======
>>>>>>> 579dc230bc3674712c8782292c6159cb762701f4
-- Contraintes pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD CONSTRAINT `paiements_ibfk_1` FOREIGN KEY (`id_trip`) REFERENCES `trips` (`id_trip`),
  ADD CONSTRAINT `paiements_ibfk_2` FOREIGN KEY (`recu_par`) REFERENCES `users` (`id_user`);

--
-- Contraintes pour la table `trips`
--
ALTER TABLE `trips`
  ADD CONSTRAINT `trips_ibfk_1` FOREIGN KEY (`id_vehicule`) REFERENCES `vehicules` (`id_vehicule`),
  ADD CONSTRAINT `trips_ibfk_2` FOREIGN KEY (`id_chauffeur`) REFERENCES `chauffeurs` (`id_chauffeur`),
  ADD CONSTRAINT `trips_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id_user`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
