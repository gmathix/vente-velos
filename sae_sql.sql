DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS velo;
DROP TABLE IF EXISTS type_velo;
DROP TABLE IF EXISTS taille;
DROP TABLE IF EXISTS etat;



CREATE TABLE taille(
   id_taille INT AUTO_INCREMENT,
   libelle_taille VARCHAR(50),
   PRIMARY KEY(id_taille)
);

CREATE TABLE type_velo(
   id_type_velo INT AUTO_INCREMENT,
   libelle_type_velo VARCHAR(50),
   PRIMARY KEY(id_type_velo)
);

CREATE TABLE utilisateur(
   id_utilisateur INT AUTO_INCREMENT,
   login VARCHAR(50),
   password VARCHAR(200),
   role VARCHAR(50),
   est_actif BOOLEAN,
   nom VARCHAR(50),
   email VARCHAR(50),
   PRIMARY KEY(id_utilisateur)
);

CREATE TABLE etat(
   id_etat INT AUTO_INCREMENT,
   libelle VARCHAR(50),
   PRIMARY KEY(id_etat)
);

CREATE TABLE velo(
   id_velo INT AUTO_INCREMENT,
   nom_velo VARCHAR(50),
   prix_velo DECIMAL(9,2),
   taille_id INT,
   type_velo_id INT,
   matiere VARCHAR(50),
   description VARCHAR(100),
   fournisseur VARCHAR(50),
   marque VARCHAR(50),
   photo VARCHAR(50),
   stock INT,
   id_taille INT NOT NULL,
   id_type_velo INT NOT NULL,
   PRIMARY KEY(id_velo),
   FOREIGN KEY(id_taille) REFERENCES taille(id_taille),
   FOREIGN KEY(id_type_velo) REFERENCES type_velo(id_type_velo)
);

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATE,
   utilisateur_id INT,
   etat_id INT,
   id_etat INT NOT NULL,
   PRIMARY KEY(id_commande),
   FOREIGN KEY(id_etat) REFERENCES etat(id_etat)
);

CREATE TABLE ligne_commande(
   id_velo INT,
   id_commande INT,
   prix DECIMAL(9,2),
   quantite INT,
   PRIMARY KEY(id_velo, id_commande),
   FOREIGN KEY(id_velo) REFERENCES velo(id_velo),
   FOREIGN KEY(id_commande) REFERENCES commande(id_commande)
);

CREATE TABLE ligne_panier(
   id_velo INT,
   id_utilisateur INT,
   quantite INT,
   date_ajout DATE,
   PRIMARY KEY(id_velo, id_utilisateur),
   FOREIGN KEY(id_velo) REFERENCES velo(id_velo),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);


-- ============================================
-- JEU DE TEST - Système de vente de vélos
-- Basé sur le fichier Pix_velos.csv
-- ============================================

-- ============================================
-- TABLE: taille
-- ============================================
INSERT INTO taille (libelle_taille) VALUES
('XS'),
('S'),
('M'),
('L'),
('XL'),
('Taille unique');

-- ============================================
-- TABLE: type_velo (catégories présentes dans le CSV)
-- ============================================
INSERT INTO type_velo (libelle_type_velo) VALUES
('BMX'),
('Ville'),
('VTT'),
('Enfant'),
('Pliant'),
('VTC'),
('Route');

-- ============================================
-- TABLE: utilisateur
-- ============================================
INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client','client2','1');
-- ============================================
-- TABLE: etat
-- ============================================
INSERT INTO etat (libelle) VALUES
('en attente'),
('expédié'),
('validé'),
('confirmé');

-- ============================================
-- TABLE: velo (18 vélos du CSV)
-- ============================================
INSERT INTO velo (nom_velo, prix_velo, matiere, description, fournisseur, marque, photo, stock, id_taille, id_type_velo) VALUES
-- BMX (1 vélo)
('Modèle 401', 100.00, 'Aluminium', 'BMX orange 20 pouces, 1 vitesse, freins patins', 'Fournisseur BMX', 'BikeShop', 'BMX1.png', 8, 6, 1),

-- Ville (7 vélos)
('Modèle 185', 500.00, 'Acier', 'Vélo ville noir 26", 7 vitesses, éclairage dynamo, panier et porte-bagage', 'Urban Bikes', 'CityCycle', 'ville1.jpg', 12, 3, 2),
('Modèle 426', 300.00, 'Acier', 'Vélo ville jaune 24", 3 vitesses, garde-boue, panier et porte-bagage', 'Urban Bikes', 'CityCycle', 'ville2.jpg', 10, 2, 2),
('Modèle 615', 450.00, 'Acier', 'Vélo ville noir 26", 3 vitesses, freins disques, éclairage dynamo', 'Urban Bikes', 'VilleConfort', 'ville3.jpg', 7, 3, 2),
('Modèle 121', 450.00, 'Acier', 'Vélo ville rose 26", 3 vitesses, freins disques, dynamo, accessoires complets', 'Urban Bikes', 'CityCycle', 'ville4.jpeg', 9, 3, 2),
('Modèle 377', 350.00, 'Acier', 'Vélo ville orange 26", 3 vitesses, éclairage dynamo, porte-bagage', 'Urban Bikes', 'VilleConfort', 'ville5.jpg', 11, 3, 2),
('Modèle 115', 350.00, 'Aluminium', 'Vélo ville bleu 28", 3 vitesses, éclairage dynamo, porte-bagage', 'Urban Bikes', 'AluminiumPro', 'ville6.jpg', 8, 4, 2),
('Modèle 435', 300.00, 'Acier', 'Vélo ville blanc 24", 3 vitesses, freins disques, équipement complet', 'Urban Bikes', 'CityCycle', 'ville7.jpg', 6, 2, 2),

-- VTT (4 vélos)
('Modèle 686', 450.00, 'Aluminium', 'VTT orange 26", 21 vitesses, freins disques', 'Mountain Gear', 'TrailPro', 'vtt1.jpeg', 5, 3, 3),
('Modèle 490', 750.00, 'Aluminium', 'VTT noir 28", 27 vitesses, freins disques, éclairage piles, garde-boue', 'Mountain Gear', 'AlpineSport', 'vtt2.jpeg', 4, 4, 3),
('Modèle 265', 600.00, 'Aluminium', 'VTT noir 26", 27 vitesses, freins patins', 'Mountain Gear', 'TrailPro', 'vtt3.jpeg', 6, 3, 3),
('Modèle 558', 800.00, 'Acier', 'VTT orange 28", 30 vitesses, freins disques haute performance', 'Mountain Gear', 'ProSport', 'vtt4.jpeg', 3, 4, 3),

-- Enfant (2 vélos)
('Modèle 675', 200.00, 'Acier', 'Vélo enfant noir 16", 5 vitesses, garde-boue', 'Kids Bikes', 'Junior', 'enfant1.jpeg', 15, 1, 4),
('Modèle 380', 300.00, 'Acier', 'Vélo enfant bleu 20", 5 vitesses, éclairage dynamo, garde-boue, panier', 'Kids Bikes', 'Junior', 'enfant2.jpeg', 12, 1, 4),

-- Pliant (1 vélo)
('Modèle 363', 1000.00, 'Acier', 'Vélo pliant bleu 16", 6 vitesses, éclairage piles, compact et pratique', 'Compact Wheels', 'FoldMaster', 'pliant1.jpeg', 5, 6, 5),

-- VTC (1 vélo)
('Modèle 331', 400.00, 'Acier', 'VTC bleu 28", 15 vitesses, éclairage dynamo, garde-boue, porte-bagage', 'Hybrid Cycles', 'Polyvalent', 'vtc1.jpeg', 7, 4, 6),

-- Route (3 vélos)
('Modèle 163', 300.00, 'Acier', 'Vélo route bleu 28", 10 vitesses, freins patins', 'Speed Bikes', 'RacePro', 'route1.jpeg', 6, 4, 7),
('Modèle 379', 250.00, 'Acier', 'Vélo route marron 28", 10 vitesses, freins patins', 'Speed Bikes', 'ClassicRoad', 'route2.jpeg', 8, 4, 7),
('Modèle 184', 400.00, 'Acier', 'Vélo route rouge 28", 15 vitesses, freins patins, performance', 'Speed Bikes', 'RacePro', 'route3.jpeg', 5, 4, 7);

-- ============================================
-- TABLE: commande
-- ============================================
INSERT INTO commande (date_achat, utilisateur_id, etat_id, id_etat) VALUES
-- Commandes client (id=2)
('2024-12-10', 2, 3, 3),  -- validé
('2025-01-05', 2, 2, 2),  -- expédié
('2025-01-22', 2, 4, 4),  -- confirmé
('2025-01-28', 2, 1, 1),  -- en attente

-- Commandes client2 (id=3)
('2024-11-15', 3, 3, 3),  -- validé
('2025-01-08', 3, 2, 2),  -- expédié
('2025-01-25', 3, 1, 1);  -- en attente

-- ============================================
-- TABLE: ligne_commande
-- ============================================
INSERT INTO ligne_commande (id_velo, id_commande, prix, quantite) VALUES
-- Commande 1 (client - validé)
(2, 1, 500.00, 1),   -- Modèle 185 ville
(9, 1, 450.00, 1),   -- Modèle 686 VTT

-- Commande 2 (client - expédié)
(10, 2, 750.00, 1),  -- Modèle 490 VTT
(13, 2, 1000.00, 1), -- Modèle 363 pliant

-- Commande 3 (client - confirmé)
(15, 3, 300.00, 1),  -- Modèle 163 route

-- Commande 4 (client - en attente)
(1, 4, 100.00, 2),   -- Modèle 401 BMX x2
(11, 4, 200.00, 1),  -- Modèle 675 enfant

-- Commande 5 (client2 - validé)
(4, 5, 450.00, 1),   -- Modèle 615 ville
(12, 5, 300.00, 1),  -- Modèle 380 enfant

-- Commande 6 (client2 - expédié)
(17, 6, 400.00, 1),  -- Modèle 184 route

-- Commande 7 (client2 - en attente)
(14, 7, 400.00, 1),  -- Modèle 331 VTC
(8, 7, 350.00, 1);   -- Modèle 115 ville

-- ============================================
-- TABLE: ligne_panier (paniers actifs)
-- ============================================
INSERT INTO ligne_panier (id_velo, id_utilisateur, quantite, date_ajout) VALUES
-- Panier client
(12, 2, 1, '2025-01-28'),  -- Modèle 558 VTT
(5, 2, 1, '2025-01-27'),   -- Modèle 121 ville
(16, 2, 1, '2025-01-26'),  -- Modèle 379 route

-- Panier client2
(3, 3, 1, '2025-01-29'),   -- Modèle 426 ville
(7, 3, 2, '2025-01-29'),   -- Modèle 435 ville x2
(11, 3, 1, '2025-01-28');  -- Modèle 265 VTT

-- ============================================
-- VÉRIFICATION DES DONNÉES INSÉRÉES
-- ============================================
SELECT 'TAILLES' as Table_Name, COUNT(*) as Nb_Lignes FROM taille
UNION ALL
SELECT 'TYPES VELO', COUNT(*) FROM type_velo
UNION ALL
SELECT 'UTILISATEURS', COUNT(*) FROM utilisateur
UNION ALL
SELECT 'ETATS', COUNT(*) FROM etat
UNION ALL
SELECT 'VELOS', COUNT(*) FROM velo
UNION ALL
SELECT 'COMMANDES', COUNT(*) FROM commande
UNION ALL
SELECT 'LIGNES COMMANDE', COUNT(*) FROM ligne_commande
UNION ALL
SELECT 'LIGNES PANIER', COUNT(*) FROM ligne_panier;

-- ============================================
-- REQUÊTES DE VÉRIFICATION DÉTAILLÉES
-- ============================================

-- Répartition des vélos par type
SELECT t.libelle_type_velo, COUNT(*) as nb_velos
FROM velo v
JOIN type_velo t ON v.id_type_velo = t.id_type_velo
GROUP BY t.libelle_type_velo
ORDER BY nb_velos DESC;

-- Commandes par état
SELECT e.libelle, COUNT(*) as nb_commandes
FROM commande c
JOIN etat e ON c.id_etat = e.id_etat
GROUP BY e.libelle;

-- velos dans les paniers
SELECT u.login, COUNT(*) as velos_panier
FROM ligne_panier lp
JOIN utilisateur u ON lp.id_utilisateur = u.id_utilisateur
GROUP BY u.login;