#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
        SELECT velo.id_velo AS id_velo, 
                nom_velo AS nom,
                quantite AS quantite,
                velo.id_taille AS id_taille,
                libelle_taille AS libelle_taille,
                prix_velo AS prix,
                stock AS stock
        FROM ligne_panier
        INNER JOIN velo ON ligne_panier.id_velo = velo.id_velo
        INNER JOIN taille ON velo.id_taille = taille.id_taille
        WHERE ligne_panier.id_utilisateur = %s
    '''

    mycursor.execute(sql, (id_client))
    velos_panier = mycursor.fetchall()

    if len(velos_panier) >= 1:
        sql = '''SELECT SUM(prix_velo * quantite) AS total
                 FROM ligne_panier 
                 INNER JOIN velo ON ligne_panier.id_velo = velo.id_velo
                 WHERE ligne_panier.id_utilisateur = %s'''
        mycursor.execute(sql, (id_client))
        prix_total = mycursor.fetchone()['total']
    else:
        prix_total = 0

    # etape 2 : selection des adresses
    sql = ''''''

    return render_template('client/boutique/panier_validation_adresses.html'
                           #, adresses=adresses
                           , velos_panier=velos_panier
                           , prix_total= prix_total
                           , validation=1
                           #, id_adresse_fav=id_adresse_fav
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()

    # choix de(s) (l')adresse(s)

    id_client = session['id_user']
    sql = ''' selection du contenu du panier de l'utilisateur '''
    items_ligne_panier = []
    # if items_ligne_panier is None or len(items_ligne_panier) < 1:
    #     flash(u'Pas d\'velos dans le ligne_panier', 'alert-warning')
    #     return redirect('/client/velo/show')
                                           # https://pynative.com/python-mysql-transaction-management-using-commit-rollback/
    #a = datetime.strptime('my date', "%b %d %Y %H:%M")

    sql = ''' creation de la commande '''

    sql = '''SELECT last_insert_id() as last_insert_id'''
    # numéro de la dernière commande
    for item in items_ligne_panier:
        sql = ''' suppression d'une ligne de panier '''
        sql = "  ajout d'une ligne de commande'"

    get_db().commit()
    flash(u'Commande ajoutée','alert-success')
    return redirect('/client/velo/show')




@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''
          SELECT 
              commande.id_commande, 
              date_achat,
              libelle, 
              SUM(ligne_commande.quantite) AS nbr_velos,
              SUM(ligne_commande.prix * ligne_commande.quantite) AS prix_total
        FROM commande
        INNER JOIN etat ON commande.id_etat = etat.id_etat
        INNER JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
        WHERE commande.utilisateur_id = %s
      GROUP BY commande.id_commande, date_achat, libelle
        ORDER BY commande.date_achat DESC
          '''
    mycursor.execute(sql, id_client)
    commandes = mycursor.fetchall()

    velos_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        print(id_commande)
        sql = '''
              SELECT utilisateur.nom   AS nom,
                     quantite          AS quantite,
                     prix              AS prix,
                     (quantite * prix) AS prix_ligne


              FROM ligne_commande
                       INNER JOIN commande ON ligne_commande.id_commande = commande.id_commande
                       INNER JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
              WHERE ligne_commande.id_commande = %s \
              '''
        mycursor.execute(sql, id_commande)
        velos_commande = mycursor.fetchall()

        # partie 2 : selection de l'adresse de livraison et de facturation de la commande selectionnée
        sql = ''' selection des adressses '''

    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , velos_commande=velos_commande
                           , commande_adresses=commande_adresses
                           )

