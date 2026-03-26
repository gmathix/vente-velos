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
    DROP TABLE IF EXISTS ligne_panier, ligne_commande, commande, declinaison_velo,
    note, commentaire, historique, liste_envie,
    velo, adresse, etat, utilisateur, type_velo, taille;
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
    ) DEFAULT CHARSET utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
    (1,'admin','admin@admin.fr',
        'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
        'ROLE_admin','admin',1),
    (2,'client','client@client.fr',
        'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
        'ROLE_client','client',1),
    (3,'client2','client2@client2.fr',
        'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
        'ROLE_client','client2',1);
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
    ) DEFAULT CHARSET utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO type_velo (libelle_type_velo) VALUES
    ('BMX'),('Ville'),('VTT'),('Enfant'),('Pliant'),('VTC'),('Route');
    '''
    mycursor.execute(sql)

    # ============================================
    # taille
    # ============================================
    sql = '''
    CREATE TABLE taille(
        id_taille INT AUTO_INCREMENT,
        libelle_taille VARCHAR(50),
        PRIMARY KEY(id_taille)
    ) DEFAULT CHARSET utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO taille (libelle_taille) VALUES
    ('XS'),('S'),('M'),('L'),('XL'),('Taille unique');
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
    ('en attente'),('expédié'),('validé'),('confirmé');
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
    ('Belfort', 'rue des raverottes',  80000, 'belfort', '2025-12-12', 2),
    ('Belfort', 'rue des belfortains', 80000, 'belfort', '2025-02-12', 2);
    '''
    mycursor.execute(sql)

    # ============================================
    # velo  (prix/stock/photo/taille -> declinaison_velo)
    # ============================================
    sql = '''
    CREATE TABLE velo(
        id_velo INT AUTO_INCREMENT,
        nom_velo VARCHAR(50),
        matiere VARCHAR(50),
        description VARCHAR(100),
        fournisseur VARCHAR(50),
        marque VARCHAR(50),
        id_type_velo INT NOT NULL,
        PRIMARY KEY(id_velo),
        FOREIGN KEY(id_type_velo) REFERENCES type_velo(id_type_velo)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO velo (nom_velo, matiere, description, fournisseur, marque, id_type_velo) VALUES
    ('BMX Orange',        'Aluminium', 'BMX orange 20 pouces, 1 vitesse, freins patins',                                'Fournisseur BMX', 'BikeShop',     1),
    ('Velo ville noir',   'Acier',     'Vélo ville noir 26", 7 vitesses, éclairage dynamo, panier et porte-bagage',     'Urban Bikes',     'CityCycle',    2),
    ('Velo ville jaune',  'Acier',     'Vélo ville jaune 24", 3 vitesses, garde-boue, panier et porte-bagage',          'Urban Bikes',     'CityCycle',    2),
    ('Velo ville noir',   'Acier',     'Vélo ville noir 26", 3 vitesses, freins disques, éclairage dynamo',             'Urban Bikes',     'VilleConfort', 2),
    ('Velo ville rose',   'Acier',     'Vélo ville rose 26", 3 vitesses, freins disques, dynamo, accessoires complets', 'Urban Bikes',     'CityCycle',    2),
    ('Velo ville orange', 'Acier',     'Vélo ville orange 26", 3 vitesses, éclairage dynamo, porte-bagage',             'Urban Bikes',     'VilleConfort', 2),
    ('Velo ville bleu',   'Aluminium', 'Vélo ville bleu 28", 3 vitesses, éclairage dynamo, porte-bagage',               'Urban Bikes',     'AluminiumPro', 2),
    ('Velo ville blanc',  'Acier',     'Vélo ville blanc 24", 3 vitesses, freins disques, équipement complet',          'Urban Bikes',     'CityCycle',    2),
    ('VTT orange',        'Aluminium', 'VTT orange 26", 21 vitesses, freins disques',                                   'Mountain Gear',   'TrailPro',     3),
    ('VTT noir',          'Aluminium', 'VTT noir 28", 27 vitesses, freins disques, éclairage piles, garde-boue',        'Mountain Gear',   'AlpineSport',  3),
    ('VTT noir',          'Aluminium', 'VTT noir 26", 27 vitesses, freins patins',                                      'Mountain Gear',   'TrailPro',     3),
    ('VTT orange',        'Acier',     'VTT orange 28", 30 vitesses, freins disques haute performance',                 'Mountain Gear',   'ProSport',     3),
    ('Velo enfant noir',  'Acier',     'Vélo enfant noir 16", 5 vitesses, garde-boue',                                  'Kids Bikes',      'Junior',       4),
    ('Velo enfant bleu',  'Acier',     'Vélo enfant bleu 20", 5 vitesses, éclairage dynamo, garde-boue, panier',        'Kids Bikes',      'Junior',       4),
    ('Velo pliant',       'Acier',     'Vélo pliant bleu 16", 6 vitesses, éclairage piles, compact et pratique',        'Compact Wheels',  'FoldMaster',   5),
    ('VTC bleu',          'Acier',     'VTC bleu 28", 15 vitesses, éclairage dynamo, garde-boue, porte-bagage',         'Hybrid Cycles',   'Polyvalent',   6),
    ('Velo route bleu',   'Acier',     'Vélo route bleu 28", 10 vitesses, freins patins',                               'Speed Bikes',     'RacePro',      7),
    ('Velo route marron', 'Acier',     'Vélo route marron 28", 10 vitesses, freins patins',                             'Speed Bikes',     'ClassicRoad',  7),
    ('Velo route rouge',  'Acier',     'Vélo route rouge 28", 15 vitesses, freins patins, performance',                 'Speed Bikes',     'RacePro',      7);
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
        id_taille INT NOT NULL,
        id_velo INT NOT NULL,
        PRIMARY KEY(id_declinaison_velo),
        FOREIGN KEY(id_taille) REFERENCES taille(id_taille),
        FOREIGN KEY(id_velo) REFERENCES velo(id_velo)
    );
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO declinaison_velo (stock, prix_declinaison, image, id_taille, id_velo) VALUES
    ( 8,   100.00, 'BMX1.jpg',      6,  1),
    (12,   500.00, 'ville1.jpg',    3,  2),
    (10,   300.00, 'ville2.jpg',    2,  3),
    ( 7,   450.00, 'ville3.jpg',    3,  4),
    ( 9,   450.00, 'ville4.jpeg',   3,  5),
    (11,   350.00, 'ville5.jpg',    3,  6),
    ( 8,   350.00, 'ville6.jpg',    4,  7),
    ( 6,   300.00, 'ville7.jpg',    2,  8),
    ( 5,   450.00, 'vtt1.jpeg',     3,  9),
    ( 4,   750.00, 'vtt2.jpeg',     4, 10),
    ( 6,   600.00, 'vtt3.jpeg',     3, 11),
    ( 3,   800.00, 'vtt4.jpeg',     4, 12),
    (15,   200.00, 'enfant1.jpeg',  1, 13),
    (12,   300.00, 'enfant2.jpeg',  1, 14),
    ( 5,  1000.00, 'pliant1.jpeg',  6, 15),
    ( 7,   400.00, 'vtc1.jpeg',     4, 16),
    ( 6,   300.00, 'route1.jpeg',   4, 17),
    ( 8,   250.00, 'route2.jpeg',   4, 18),
    ( 5,   400.00, 'route3.jpeg',   4, 19);
    '''
    mycursor.execute(sql)

    # ============================================
    # commande
    # ============================================
    sql = '''
    CREATE TABLE commande(
        id_commande INT AUTO_INCREMENT,
        date_achat DATE,
        utilisateur_id INT,
        etat_id INT,
        id_etat INT NOT NULL,
        id_adresse INT NOT NULL,
        id_adresse_1 INT NOT NULL,
        PRIMARY KEY(id_commande),
        FOREIGN KEY(id_etat) REFERENCES etat(id_etat),
        FOREIGN KEY(id_adresse) REFERENCES adresse(id_adresse),
        FOREIGN KEY(id_adresse_1) REFERENCES adresse(id_adresse)
    );
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO commande (date_achat, utilisateur_id, id_etat, id_adresse, id_adresse_1) VALUES
    ('2024-12-10', 2, 3, 1, 1),
    ('2025-01-05', 2, 2, 1, 1),
    ('2025-01-22', 2, 4, 1, 1),
    ('2025-01-28', 2, 1, 1, 1),
    ('2024-11-15', 3, 3, 2, 2),
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
    (1,  2,   500.00, 1),
    (1,  9,   450.00, 1),
    (2, 10,   750.00, 1),
    (2, 15,  1000.00, 1),
    (3, 17,   300.00, 1),
    (4,  1,   100.00, 20),
    (4, 13,   200.00, 1),
    (5,  4,   450.00, 1),
    (5, 14,   300.00, 1),
    (6, 17,   400.00, 1),
    (7, 16,   400.00, 1),
    (7,  8,   350.00, 1);
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
    (2, 11, 1, '2025-01-28'),
    (2,  5, 1, '2025-01-27'),
    (2, 18, 1, '2025-01-26'),
    (3,  3, 1, '2025-01-29'),
    (3,  7, 2, '2025-01-29'),
    (3, 11, 1, '2025-01-28');
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

    # ============================================
    # commentaire
    # ============================================
    sql = '''
    CREATE TABLE commentaire(
        id_velo INT,
        id_utilisateur INT,
        date_publication DATE,
        valider BOOLEAN,
        commentaire VARCHAR(50),
        PRIMARY KEY(id_velo, id_utilisateur, date_publication),
        FOREIGN KEY(id_velo) REFERENCES velo(id_velo),
        FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
    );
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

    get_db().commit()
    return redirect('/')