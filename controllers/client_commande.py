# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session
from datetime import datetime

from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Articles dans le panier
    sql = '''
        SELECT D.id_declinaison_velo AS id_declinaison_velo,
               V.nom_velo AS nom,
               L.quantite AS quantite,
               D.prix_declinaison AS prix,
               D.stock AS stock,
               T.libelle_taille AS libelle_taille
        FROM ligne_panier L
        JOIN declinaison_velo D ON L.id_declinaison_velo = D.id_declinaison_velo
        JOIN velo V ON D.id_velo = V.id_velo
        JOIN taille T ON D.id_taille = T.id_taille
        WHERE L.id_utilisateur = %s
    '''
    mycursor.execute(sql, id_client)
    velos_panier = mycursor.fetchall()

    # Total du panier en SQL
    sql = '''
        SELECT SUM(D.prix_declinaison * L.quantite) AS total
        FROM ligne_panier L
        JOIN declinaison_velo D ON L.id_declinaison_velo = D.id_declinaison_velo
        WHERE L.id_utilisateur = %s
    '''
    mycursor.execute(sql, id_client)
    prix_total = mycursor.fetchone()['total']

    # Adresses valides du client, favorite en premier
    sql = '''
        SELECT id_adresse, nom, rue, code_postal, ville, favori
        FROM adresse
        WHERE id_utilisateur = %s AND valide = TRUE
        ORDER BY favori DESC
    '''
    mycursor.execute(sql, id_client)
    adresses = mycursor.fetchall()

    # Id de l'adresse favorite pour la preselectionnner dans le formulaire
    sql = '''
        SELECT id_adresse FROM adresse
        WHERE id_utilisateur = %s AND favori = TRUE AND valide = TRUE
    '''
    mycursor.execute(sql, id_client)
    fav = mycursor.fetchone()
    id_adresse_fav = 0
    if fav != None:
        id_adresse_fav = fav['id_adresse']

    return render_template('client/boutique/panier_validation_adresses.html',
                           adresses=adresses,
                           velos_panier=velos_panier,
                           prix_total=prix_total,
                           validation=1,
                           id_adresse_fav=id_adresse_fav)


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    id_adresse_livraison   = request.form.get('id_adresse_livraison')
    adresse_identique      = request.form.get('adresse_identique')
    id_adresse_facturation = request.form.get('id_adresse_facturation')

    # Si case cochee : adresse facturation = adresse livraison
    if adresse_identique == 'adresse_identique':
        id_adresse_facturation = id_adresse_livraison

    # Articles du panier
    sql = '''
        SELECT L.id_declinaison_velo AS id_declinaison_velo,
               L.quantite            AS quantite,
               D.prix_declinaison    AS prix
        FROM ligne_panier L
        JOIN declinaison_velo D ON L.id_declinaison_velo = D.id_declinaison_velo
        WHERE L.id_utilisateur = %s
    '''
    mycursor.execute(sql, id_client)
    items_panier = mycursor.fetchall()

    # Etat "en attente"
    sql = ''' SELECT id_etat FROM etat WHERE libelle = 'en attente' '''
    mycursor.execute(sql)
    id_etat = mycursor.fetchone()['id_etat']

    # Creation de la commande
    sql = '''
        INSERT INTO commande (date_achat, utilisateur_id, id_etat, id_adresse, id_adresse_1)
        VALUES (%s, %s, %s, %s, %s)
    '''
    mycursor.execute(sql, (datetime.now(), id_client, id_etat,
                           id_adresse_livraison, id_adresse_facturation))

    sql = ''' SELECT last_insert_id() AS last_insert_id '''
    mycursor.execute(sql)
    id_commande = mycursor.fetchone()['last_insert_id']

    # Lignes de commande + vidage du panier
    for item in items_panier:
        sql = '''
            INSERT INTO ligne_commande (id_commande, id_declinaison_velo, prix, quantite)
            VALUES (%s, %s, %s, %s)
        '''
        mycursor.execute(sql, (id_commande, item['id_declinaison_velo'],
                               item['prix'], item['quantite']))

        sql = '''
            DELETE FROM ligne_panier
            WHERE id_declinaison_velo = %s AND id_utilisateur = %s
        '''
        mycursor.execute(sql, (item['id_declinaison_velo'], id_client))

    # Consigne 4 : l'adresse de livraison utilisee devient la nouvelle favorite
    sql = ''' UPDATE adresse SET favori = FALSE WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)

    sql = ''' UPDATE adresse SET favori = TRUE WHERE id_adresse = %s AND id_utilisateur = %s '''
    mycursor.execute(sql, (id_adresse_livraison, id_client))

    get_db().commit()
    flash(u'Commande ajoutee avec succes.', 'alert-success')
    return redirect('/client/velo/show')


@client_commande.route('/client/commande/show', methods=['GET', 'POST'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Liste de toutes les commandes du client
    sql = '''
        SELECT commande.id_commande,
               commande.date_achat,
               etat.libelle,
               SUM(ligne_commande.quantite)               AS nbr_velos,
               SUM(ligne_commande.prix * ligne_commande.quantite) AS prix_total
        FROM commande
        JOIN etat          ON commande.id_etat = etat.id_etat
        JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
        WHERE commande.utilisateur_id = %s
        GROUP BY commande.id_commande, commande.date_achat, etat.libelle
        ORDER BY commande.date_achat DESC
    '''
    mycursor.execute(sql, id_client)
    commandes = mycursor.fetchall()

    velos_commande   = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)

    if id_commande != None:
        # Detail des articles de la commande selectionnee
        sql = '''
            SELECT V.nom_velo                             AS nom,
                   LC.quantite                            AS quantite,
                   LC.prix                               AS prix,
                   (LC.quantite * LC.prix)               AS prix_ligne
            FROM ligne_commande LC
            JOIN commande        C  ON LC.id_commande = C.id_commande
            JOIN declinaison_velo D  ON LC.id_declinaison_velo = D.id_declinaison_velo
            JOIN velo            V  ON D.id_velo = V.id_velo
            WHERE LC.id_commande = %s AND C.utilisateur_id = %s
        '''
        mycursor.execute(sql, (id_commande, id_client))
        velos_commande = mycursor.fetchall()

        # Consigne 5 : adresses de livraison et facturation de la commande
        # Consigne 6 : IF() en SQL pour detecter si les deux adresses sont identiques
        sql = '''
            SELECT A_LIV.nom AS nom_livraison,
                   A_LIV.rue AS rue_livraison,
                   A_LIV.code_postal  AS code_postal_livraison,
                   A_LIV.ville        AS ville_livraison,
                   A_FACT.nom         AS nom_facturation,
                   A_FACT.rue         AS rue_facturation,
                   A_FACT.code_postal AS code_postal_facturation,
                   A_FACT.ville       AS ville_facturation,
                   IF(C.id_adresse = C.id_adresse_1,
                      'adresse_identique',
                      'adresse_non_identique') AS adresse_identique
            FROM commande C
            JOIN adresse A_LIV  ON C.id_adresse   = A_LIV.id_adresse
            JOIN adresse A_FACT ON C.id_adresse_1 = A_FACT.id_adresse
            WHERE C.id_commande = %s AND C.utilisateur_id = %s
        '''
        mycursor.execute(sql, (id_commande, id_client))
        commande_adresses = mycursor.fetchone()

    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           velos_commande=velos_commande,
                           commande_adresses=commande_adresses)