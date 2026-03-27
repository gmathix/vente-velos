# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                        template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()

    sql = '''
    DROP TABLE IF EXISTS note, liste_envie, historique, commentaire, ligne_panier, ligne_commande,
    declinaison_velo, commande, velo, adresse, taille,
    etat, utilisateur, type_velo, couleur;

    '''
    mycursor.execute(sql)

    # ============================================
    # type_velo
    # ============================================
    sql = '''
    CREATE TABLE type_velo(
   id_type_velo INT AUTO_INCREMENT,
   libelle_type_velo VARCHAR(50),
   PRIMARY KEY(id_type_velo)
);
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO type_velo (libelle_type_velo) VALUES
    ('BMX'),    -- 1
    ('Ville'),  -- 2
    ('VTT'),    -- 3
    ('Enfant'), -- 4
    ('Pliant'), -- 5
    ('VTC'),    -- 6
    ('Route');  -- 7
    '''
    mycursor.execute(sql)

    # ============================================
    # utilisateur
    # ============================================
    sql = '''
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
          '''
    mycursor.execute(sql)
    sql = '''
          INSERT INTO utilisateur (id_utilisateur, login, email, password, role, nom, est_actif) VALUES
            (1, 'admin',   'admin@admin.fr',
                'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
                'ROLE_admin', 'admin', 1),
            (2, 'client',  'client@client.fr',
                'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
                'ROLE_client', 'client', 1),
            (3, 'client2', 'client2@client2.fr',
                'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
                'ROLE_client', 'client2', 1);
          '''
    mycursor.execute(sql)

    # ============================================
    # etat
    # ============================================
    sql = '''
    CREATE TABLE etat(
        id_etat INT AUTO_INCREMENT,
        libelle VARCHAR(50),
        PRIMARY KEY(id_etat)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO etat (libelle) VALUES
        ('en attente'),
        ('expédié')    
    '''
    mycursor.execute(sql)

    # ============================================
    # taille
    # ============================================
    sql = '''
          CREATE TABLE taille(
           id_taille INT AUTO_INCREMENT,
           libelle VARCHAR(50),
           code_taille INT,
           PRIMARY KEY(id_taille)
        );
          '''
    mycursor.execute(sql)
    sql = '''
          INSERT INTO taille (libelle, code_taille) VALUES
                ('16 pouces', 16),  -- 1 : enfants petits
                ('20 pouces', 20),  -- 2 : BMX, enfants grands
                ('24 pouces', 24),  -- 3 : junior / petits adultes
                ('26 pouces', 26),  -- 4 : adulte standard VTT/ville
                ('28 pouces', 28),  -- 5 : adulte route/ville/VTC
                ('29 pouces', 29),  -- 6 : VTT grande roue
                ('Taille unique', 0); -- 7 : pliant
          '''
    mycursor.execute(sql)

    # ============================================
    # adresse
    # ============================================
    sql = '''
    CREATE TABLE adresse(
       id_adresse INT AUTO_INCREMENT,
       nom VARCHAR(50),
       rue VARCHAR(50),
       code_postal INT,
       ville VARCHAR(50),
       date_utilisation DATE,
       id_utilisateur INT NOT NULL,
       PRIMARY KEY(id_adresse),
       FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
    );

    '''
    mycursor.execute(sql)
    sql = '''
        INSERT INTO adresse (nom, rue, code_postal, ville, date_utilisation, id_utilisateur) VALUES
        ('67', 'rue des raverottes',  80000, 'belfort', '2025-12-12', 2), -- 1
        ('25', 'rue des belfortains', 80000, 'belfort', '2025-02-12', 2); -- 2
    '''
    mycursor.execute(sql)

    # ============================================
    # couleur
    # ============================================
    sql = '''
          CREATE TABLE couleur(
           id_couleur INT AUTO_INCREMENT,
           libelle VARCHAR(50),
           code_couleur INT,
           PRIMARY KEY(id_couleur)
        );
          '''
    mycursor.execute(sql)
    sql = '''
          INSERT INTO couleur (libelle, code_couleur) VALUES
                ('Orange',  16737792),  -- 1  #FF6600
                ('Noir',           0),  -- 2  #000000
                ('Jaune',   16766720),  -- 3  #FFD700
                ('Blanc',   16777215),  -- 4  #FFFFFF
                ('Rose',    16738740),  -- 5  #FF69B4
                ('Rouge',   16711680),  -- 6  #FF0000
                ('Bleu',    2003199),   -- 7  #1E90FF
                ('Gris',    8421504),   -- 8  #808080
                ('Marron',  9127187);   -- 9  #8B4513
          '''
    mycursor.execute(sql)


    # ============================================
    # velo
    # ============================================
    sql = '''
    CREATE TABLE velo(
       id_velo INT AUTO_INCREMENT,
       nom_velo VARCHAR(50),
       prix_velo DECIMAL(9,2),
       matiere VARCHAR(50),
       description VARCHAR(100),
       fournisseur VARCHAR(50),
       marque VARCHAR(50),
        image VARCHAR(50),
       id_type_velo INT NOT NULL,
       PRIMARY KEY(id_velo),
       FOREIGN KEY(id_type_velo) REFERENCES type_velo(id_type_velo)
    );
    '''

    mycursor.execute(sql)
    sql = '''
        INSERT INTO velo (nom_velo, prix_velo, matiere, description, fournisseur, marque, image, id_type_velo) VALUES
                -- BMX
                ('BMX Orange',        100.00, 'Aluminium', 'BMX 20 pouces, 1 vitesse, freins patins',                              'Fournisseur BMX', 'BikeShop',     'BMX1.jpg',  1), -- 1
                -- Ville
                ('Velo ville noir',   500.00, 'Acier',     'Vélo ville 26", 7 vitesses, éclairage dynamo, panier et porte-bagage', 'Urban Bikes',     'CityCycle',   'ville1.jpg',  2), -- 2
                ('Velo ville jaune',  300.00, 'Acier',     'Vélo ville 24", 3 vitesses, garde-boue, panier et porte-bagage',       'Urban Bikes',     'CityCycle',    'ville2.jpg',2), -- 3
                ('Velo ville noir',   450.00, 'Acier',     'Vélo ville 26", 3 vitesses, freins disques, éclairage dynamo',         'Urban Bikes',     'VilleConfort', 'ville3.jpg',  2), -- 4
                ('Velo ville rose',   450.00, 'Acier',     'Vélo ville 26", 3 vitesses, freins disques, dynamo, acc. complets',    'Urban Bikes',     'CityCycle',   'ville4.jpeg',  2), -- 5
                ('Velo ville orange', 350.00, 'Acier',     'Vélo ville 26", 3 vitesses, éclairage dynamo, porte-bagage',           'Urban Bikes',     'VilleConfort', 'ville5.jpg', 2), -- 6
                ('Velo ville bleu',   350.00, 'Aluminium', 'Vélo ville 28", 3 vitesses, éclairage dynamo, porte-bagage',           'Urban Bikes',     'AluminiumPro','ville6.jpg',   2), -- 7
                ('Velo ville blanc',  300.00, 'Acier',     'Vélo ville 24", 3 vitesses, freins disques, équipement complet',       'Urban Bikes',     'CityCycle',   'ville7.jpg',  2), -- 8
                -- VTT
                ('VTT orange',        450.00, 'Aluminium', 'VTT 26", 21 vitesses, freins disques',                                 'Mountain Gear',   'TrailPro',  'vtt1.jpeg',     3), -- 9
                ('VTT noir',          750.00, 'Aluminium', 'VTT 28", 27 vitesses, freins disques, éclairage piles, garde-boue',    'Mountain Gear',   'AlpineSport', 'vtt2.jpeg',   3), -- 10
                ('VTT noir',          600.00, 'Aluminium', 'VTT 26", 27 vitesses, freins patins',                                  'Mountain Gear',   'TrailPro',    'vtt3.jpeg',  3), -- 11
                ('VTT orange',        800.00, 'Acier',     'VTT 28", 30 vitesses, freins disques haute performance',               'Mountain Gear',   'ProSport',   'vtt4.jpeg',     3), -- 12
                -- Enfant
                ('Velo enfant noir',  200.00, 'Acier',     'Vélo enfant 16", 5 vitesses, garde-boue',                              'Kids Bikes',      'Junior',     'enfant1.jpeg',  4), -- 13
                ('Velo enfant bleu',  300.00, 'Acier',     'Vélo enfant 20", 5 vitesses, éclairage dynamo, garde-boue, panier',    'Kids Bikes',      'Junior',     'enfant2.jpeg',   4), -- 14
                -- Pliant
                ('Velo pliant',      1000.00, 'Acier',     'Vélo pliant 16", 6 vitesses, éclairage piles, compact et pratique',   'Compact Wheels',  'FoldMaster', 'pliant1.jpeg',  5), -- 15
                -- VTC
                ('VTC bleu',          400.00, 'Acier',     'VTC 28", 15 vitesses, éclairage dynamo, garde-boue, porte-bagage',     'Hybrid Cycles',   'Polyvalent',   'vtc1.jpeg',6), -- 16
                -- Route
                ('Velo route bleu',   300.00, 'Acier',     'Vélo route 28", 10 vitesses, freins patins',                           'Speed Bikes',     'RacePro',   'route1.jpeg',   7), -- 17
                ('Velo route marron', 250.00, 'Acier',     'Vélo route 28", 10 vitesses, freins patins',                           'Speed Bikes',     'ClassicRoad',  'route2.jpeg', 7), -- 18
                ('Velo route rouge',  400.00, 'Acier',     'Vélo route 28", 15 vitesses, freins patins, performance',              'Speed Bikes',     'RacePro',    'route3.jpeg',   7); -- 19
'''
    mycursor.execute(sql)




    # ============================================
    # declinaison_velo
    # ============================================
    sql = '''
    CREATE TABLE declinaison_velo(
       id_declinaison_velo INT AUTO_INCREMENT,
       stock INT,
       prix_declinaison DECIMAL(15,2),
       image VARCHAR(50),
       utilisable BOOLEAN DEFAULT TRUE,
       id_couleur INT,
       id_taille INT,
       id_velo INT NOT NULL,
       PRIMARY KEY(id_declinaison_velo),
       FOREIGN KEY(id_couleur) REFERENCES couleur(id_couleur),
       FOREIGN KEY(id_taille) REFERENCES taille(id_taille),
       FOREIGN KEY(id_velo) REFERENCES velo(id_velo)
    );
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO declinaison_velo (id_velo, stock, prix_declinaison, image, id_couleur, id_taille) VALUES
        -- Velo 1 : BMX Orange — décl 1 et 2
        (1,  8,  100.00, 'BMX1.jpg',      1, 2),  -- decl  1 : Orange  / 20"
        (1,  5,  100.00, 'BMX1.jpg',      2, 2),  -- decl  2 : Noir    / 20"
        -- Velo 2 : Velo ville noir CityCycle — décl 3 et 4
        (2, 12,  500.00, 'ville1.jpg',    2, 4),  -- decl  3 : Noir    / 26"
        (2,  6,  500.00, 'ville1.jpg',    8, 4),  -- decl  4 : Gris    / 26"
        -- Velo 3 : Velo ville jaune CityCycle — décl 5 et 6
        (3, 10,  300.00, 'ville2.jpg',    3, 3),  -- decl  5 : Jaune   / 24"
        (3,  7,  300.00, 'ville2.jpg',    4, 3),  -- decl  6 : Blanc   / 24"
        -- Velo 4 : Velo ville noir VilleConfort — décl 7 et 8
        (4,  7,  450.00, 'ville3.jpg',    2, 4),  -- decl  7 : Noir    / 26"
        (4,  4,  470.00, 'ville3.jpg',    2, 5),  -- decl  8 : Noir    / 28"  (+20€)
        -- Velo 5 : Velo ville rose — décl 9 et 10
        (5,  9,  450.00, 'ville4.jpeg',   5, 4),  -- decl  9 : Rose    / 26"
        (5,  5,  450.00, 'ville4.jpeg',   4, 4),  -- decl 10 : Blanc   / 26"
        -- Velo 6 : Velo ville orange — décl 11 et 12
        (6, 11,  350.00, 'ville5.jpg',    1, 4),  -- decl 11 : Orange  / 26"
        (6,  6,  350.00, 'ville5.jpg',    6, 4),  -- decl 12 : Rouge   / 26"
        -- Velo 7 : Velo ville bleu AluminiumPro — décl 13 et 14
        (7,  8,  350.00, 'ville6.jpg',    7, 5),  -- decl 13 : Bleu    / 28"
        (7,  4,  350.00, 'ville6.jpg',    2, 5),  -- decl 14 : Noir    / 28"
        -- Velo 8 : Velo ville blanc — décl 15 et 16
        (8,  6,  300.00, 'ville7.jpg',    4, 3),  -- decl 15 : Blanc   / 24"
        (8,  4,  300.00, 'ville7.jpg',    8, 3),  -- decl 16 : Gris    / 24"
        -- Velo 9 : VTT orange TrailPro — décl 17, 18 et 19
        (9,  5,  450.00, 'vtt1.jpeg',     1, 4),  -- decl 17 : Orange  / 26"
        (9,  3,  450.00, 'vtt1.jpeg',     2, 4),  -- decl 18 : Noir    / 26"
        (9,  3,  480.00, 'vtt1.jpeg',     1, 6),  -- decl 19 : Orange  / 29"  (+30€)
        -- Velo 10 : VTT noir AlpineSport — décl 20 et 21
        (10, 4,  750.00, 'vtt2.jpeg',     2, 5),  -- decl 20 : Noir    / 28"
        (10, 2,  780.00, 'vtt2.jpeg',     2, 6),  -- decl 21 : Noir    / 29"  (+30€)
        -- Velo 11 : VTT noir TrailPro — décl 22 et 23
        (11, 6,  600.00, 'vtt3.jpeg',     2, 4),  -- decl 22 : Noir    / 26"
        (11, 3,  630.00, 'vtt3.jpeg',     2, 6),  -- decl 23 : Noir    / 29"  (+30€)
        -- Velo 12 : VTT orange ProSport — décl 24 et 25
        (12, 3,  800.00, 'vtt4.jpeg',     1, 5),  -- decl 24 : Orange  / 28"
        (12, 2,  830.00, 'vtt4.jpeg',     1, 6),  -- decl 25 : Orange  / 29"  (+30€)
        -- Velo 13 : Velo enfant noir — décl 26 et 27
        (13, 15, 200.00, 'enfant1.jpeg',  2, 1),  -- decl 26 : Noir    / 16"
        (13,  8, 200.00, 'enfant1.jpeg',  7, 1),  -- decl 27 : Bleu    / 16"
        -- Velo 14 : Velo enfant bleu — décl 28 et 29
        (14, 12, 300.00, 'enfant2.jpeg',  7, 2),  -- decl 28 : Bleu    / 20"
        (14,  7, 300.00, 'enfant2.jpeg',  6, 2),  -- decl 29 : Rouge   / 20"
        -- Velo 15 : Velo pliant — décl 30 et 31
        (15,  5, 1000.00, 'pliant1.jpeg', 7, 7),  -- decl 30 : Bleu    / Taille unique
        (15,  3, 1000.00, 'pliant1.jpeg', 2, 7),  -- decl 31 : Noir    / Taille unique
        -- Velo 16 : VTC bleu — décl 32 et 33
        (16,  7, 400.00, 'vtc1.jpeg',     7, 5),  -- decl 32 : Bleu    / 28"
        (16,  4, 400.00, 'vtc1.jpeg',     2, 5),  -- decl 33 : Noir    / 28"
        -- Velo 17 : Velo route bleu — décl 34 et 35
        (17,  6, 300.00, 'route1.jpeg',   7, 5),  -- decl 34 : Bleu    / 28"
        (17,  4, 300.00, 'route1.jpeg',   6, 5),  -- decl 35 : Rouge   / 28"
        -- Velo 18 : Velo route marron — décl 36 et 37
        (18,  8, 250.00, 'route2.jpeg',   9, 5),  -- decl 36 : Marron  / 28"
        (18,  5, 250.00, 'route2.jpeg',   2, 5),  -- decl 37 : Noir    / 28"
        -- Velo 19 : Velo route rouge — décl 38 et 39
        (19,  5, 400.00, 'route3.jpeg',   6, 5),  -- decl 38 : Rouge   / 28"
        (19,  3, 400.00, 'route3.jpeg',   2, 5);  -- decl 39 : Noir    / 28"

    '''
    mycursor.execute(sql)

    # ============================================
    # commande
    # ============================================
    sql = '''
          CREATE TABLE commande \
          ( \
              id_commande    INT AUTO_INCREMENT, \
              date_achat     DATE, \
              id_utilisateur INT NOT NULL, \
              id_etat        INT NOT NULL, \
              id_adresse     INT NOT NULL, \
              id_adresse_1   INT NOT NULL, \
              PRIMARY KEY (id_commande), \
              FOREIGN KEY (id_utilisateur) REFERENCES utilisateur (id_utilisateur), \
              FOREIGN KEY (id_etat) REFERENCES etat (id_etat), \
              FOREIGN KEY (id_adresse) REFERENCES adresse (id_adresse), \
              FOREIGN KEY (id_adresse_1) REFERENCES adresse (id_adresse)
          ); \
          '''
    mycursor.execute(sql)
    sql = '''
     INSERT INTO commande (date_achat, id_utilisateur, id_etat, id_adresse, id_adresse_1) VALUES
        ('2024-12-10', 2, 2, 1, 1),
        ('2025-01-05', 2, 2, 1, 1),
        ('2025-01-22', 2, 2, 1, 1),
        ('2025-01-28', 2, 1, 1, 1),  
        ('2024-11-15', 3, 2, 2, 2), 
        ('2025-01-08', 3, 2, 2, 2), 
        ('2025-01-25', 3, 1, 2, 2);  
          '''
    mycursor.execute(sql)



    # ============================================
    # ligne_commande
    # ============================================
    sql = '''
    CREATE TABLE ligne_commande(
       id_commande INT,
       id_declinaison_velo INT,
       prix DECIMAL(9,2),
       quantite INT,
       PRIMARY KEY(id_commande, id_declinaison_velo),
       FOREIGN KEY(id_commande) REFERENCES commande(id_commande),
       FOREIGN KEY(id_declinaison_velo) REFERENCES declinaison_velo(id_declinaison_velo)
    );
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO ligne_commande (id_commande, id_declinaison_velo, prix, quantite) VALUES
        -- Commande 1 (client - validé)
        (1,   3,   500.00, 1),  -- Velo ville noir / Noir 26"
        (1, 17,   450.00, 1),  -- VTT orange TrailPro / Orange 26"
        -- Commande 2 (client - expédié)
        (2,  20,   750.00, 1),  -- VTT noir AlpineSport / Noir 28"
        (2, 30,  1000.00, 1),  -- Velo pliant / Bleu taille unique
        -- Commande 3 (client - confirmé)
        (3, 34,   300.00, 1),  -- Velo route bleu / Bleu 28"
        -- Commande 4 (client - en attente)
        (4,    1,   100.00, 20), -- BMX Orange / Orange 20" x20
        (4, 26,   200.00, 1),  -- Velo enfant noir / Noir 16"
        -- Commande 5 (client2 - validé)
        (5,   7,   450.00, 1),  -- Velo ville noir VilleConfort / Noir 26"
        (5, 28,   300.00, 1),  -- Velo enfant bleu / Bleu 20"
        -- Commande 6 (client2 - expédié)
        (6,  34,   300.00, 1),  -- Velo route bleu / Bleu 28"
        -- Commande 7 (client2 - en attente)
        (7,  32,   400.00, 1),  -- VTC bleu / Bleu 28"
        (7,   15,   300.00, 1);  -- Velo ville blanc / Blanc 24"

    '''
    mycursor.execute(sql)

    # ============================================
    # ligne_panier
    # ============================================
    sql = '''
     CREATE TABLE ligne_panier(
       id_utilisateur INT,
       id_declinaison_velo INT,
       quantite INT,
       date_ajout DATE,
       PRIMARY KEY(id_utilisateur, id_declinaison_velo),
       FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur),
       FOREIGN KEY(id_declinaison_velo) REFERENCES declinaison_velo(id_declinaison_velo)
    );
    '''
    mycursor.execute(sql)
    sql = '''
        INSERT INTO ligne_panier (id_utilisateur, id_declinaison_velo, quantite, date_ajout) VALUES
        -- Panier client (id=2)
        (2, 22, 1, '2025-01-28'),  -- VTT noir TrailPro / Noir 26"
        (2,    9, 1, '2025-01-27'),  -- Velo ville rose / Rose 26"
        (2,  36, 1, '2025-01-26'),  -- Velo route marron / Marron 28"
        -- Panier client2 (id=3)
        (3,   5, 1, '2025-01-29'),  -- Velo ville jaune / Jaune 24"
        (3, 13, 2, '2025-01-29'),  -- Velo ville bleu / Bleu 28" x2
        (3, 22, 1, '2025-01-28');  -- VTT noir TrailPro / Noir 26"
    '''
    mycursor.execute(sql)

    # ============================================
    # commentaire
    # ============================================
    sql = '''
          CREATE TABLE commentaire \
          ( \
              id_velo          INT, \
              id_utilisateur   INT, \
              date_publication DATE, \
              valider          BOOLEAN, \
              commentaire      VARCHAR(50), \
              PRIMARY KEY (id_velo, id_utilisateur, date_publication), \
              FOREIGN KEY (id_velo) REFERENCES velo (id_velo), \
              FOREIGN KEY (id_utilisateur) REFERENCES utilisateur (id_utilisateur)
          ); \
          '''
    mycursor.execute(sql)
    sql = '''
        INSERT INTO commentaire (id_velo, id_utilisateur, date_publication, valider, commentaire) VALUES
            ( 2, 2, '2025-01-12', 1, 'Très bon vélo de ville, solide.'),
            ( 9, 2, '2025-01-20', 1, 'VTT performant, bon rapport qualité-prix.'),
            (10, 2, '2025-02-01', 0, 'Freins disques excellents.'),
            ( 4, 3, '2024-12-01', 1, 'Correct pour un usage quotidien.'),
            (14, 3, '2025-01-10', 1, 'Mon enfant adore ce vélo !'),
            (17, 3, '2025-01-15', 1, 'Bon vélo de route pour débuter.');

          '''
    mycursor.execute(sql)

    # ============================================
    # historique
    # ============================================
    sql = '''
         CREATE TABLE historique(
           id_velo INT,
           id_utilisateur INT,
           date_consultation DATE,
           PRIMARY KEY(id_velo, id_utilisateur, date_consultation),
           FOREIGN KEY(id_velo) REFERENCES velo(id_velo),
           FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        );
          '''
    mycursor.execute(sql)
    sql = '''
        INSERT INTO historique (id_velo, id_utilisateur, date_consultation) VALUES
            ( 1, 2, '2025-01-25'),
            ( 2, 2, '2025-01-25'),
            ( 9, 2, '2025-01-26'),
            (10, 2, '2025-01-26'),
            (15, 2, '2025-01-27'),
            ( 3, 3, '2025-01-28'),
            ( 4, 3, '2025-01-28'),
            ( 7, 3, '2025-01-29'),
            (12, 3, '2025-01-29'),
            (17, 3, '2025-01-30');
          '''
    mycursor.execute(sql)

    # ============================================
    # liste_envie
    # ============================================
    sql = '''
          CREATE TABLE liste_envie(
           id_velo INT,
           id_utilisateur INT,
           date_update DATE,
           PRIMARY KEY(id_velo, id_utilisateur, date_update),
           FOREIGN KEY(id_velo) REFERENCES velo(id_velo),
           FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        );
          '''
    mycursor.execute(sql)
    sql = '''
        INSERT INTO liste_envie (id_velo, id_utilisateur, date_update) VALUES
            (10, 2, '2025-01-20'),
            (15, 2, '2025-01-22'),
            (19, 2, '2025-01-24'),
            (12, 3, '2025-01-25'),
            (16, 3, '2025-01-27'),
            ( 5, 3, '2025-01-29');
          '''
    mycursor.execute(sql)



    # ============================================
    # note
    # ============================================
    sql = '''
    CREATE TABLE note(
       id_velo INT,
       id_utilisateur INT,
       note DECIMAL(15,2),
       PRIMARY KEY(id_velo, id_utilisateur),
       FOREIGN KEY(id_velo) REFERENCES velo(id_velo),
       FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
    );
    '''
    mycursor.execute(sql)
    sql = '''
        INSERT INTO note (id_velo, id_utilisateur, note) VALUES
        ( 2, 2, 4.5),
        ( 9, 2, 4.0),
        (10, 2, 5.0),
        ( 4, 3, 3.5),
        (14, 3, 4.5),
        (17, 3, 4.0),
        ( 1, 2, 3.0),
        (15, 2, 5.0);
    '''
    mycursor.execute(sql)




    get_db().commit()
    return redirect('/')