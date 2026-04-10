# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                           template_folder='templates')


@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get', 'post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']

    sql = '''
          SELECT commande.id_commande                               AS id_commande,
                 login                                              AS login,
                 date_achat                                         AS date_achat,
                 SUM(quantite)                                      AS nbr_velos,
                 SUM(ligne_commande.prix * ligne_commande.quantite) AS prix_total,
                 libelle                                            AS libelle
          FROM commande
                   INNER JOIN utilisateur ON commande.id_utilisateur = utilisateur.id_utilisateur
                   INNER JOIN etat ON commande.id_etat = etat.id_etat
                   RIGHT JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
          GROUP BY login, date_achat, libelle, commande.id_commande 
            ORDER BY etat.libelle ASC, commande.date_achat ASC
          '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    velos_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)

    if id_commande != None:
        sql = '''
            SELECT V.nom_velo                         AS nom,
                   L.quantite                         AS quantite,
                   L.prix                             AS prix,
                   (L.quantite * L.prix)              AS prix_ligne,
                   D.id_taille                        AS id_taille,
                   D.id_couleur                       AS id_couleur,
                   couleur.libelle                    AS libelle_couleur,
                   taille.libelle                     AS libelle_taille,
                   COUNT(D_COUNT.id_declinaison_velo) AS nb_declinaisons
                
            FROM ligne_commande AS L
                
            JOIN commande C ON L.id_commande = C.id_commande
            JOIN utilisateur U ON C.id_utilisateur = U.id_utilisateur
            JOIN declinaison_velo D ON L.id_declinaison_velo = D.id_declinaison_velo
            JOIN velo V ON D.id_velo = V.id_velo
            JOIN couleur ON D.id_couleur = couleur.id_couleur
            JOIN taille ON D.id_taille = taille.id_taille
            RIGHT JOIN declinaison_velo D_COUNT ON V.id_velo = D_COUNT.id_velo
                
            WHERE L.id_commande = %s
            GROUP BY V.nom_velo, quantite, prix, quantite, prix, D.id_taille, D.id_couleur, couleur.libelle, taille.libelle 
              '''
        mycursor.execute(sql, id_commande)
        velos_commande = mycursor.fetchall()

        # Adresses de livraison et de facturation de la commande
        # IF() en SQL pour detecter si les deux adresses sont identiques
        sql = '''
              SELECT A_LIV.nom                   AS nom_livraison,
                     A_LIV.rue                   AS rue_livraison,
                     A_LIV.code_postal           AS code_postal_livraison,
                     A_LIV.ville                 AS ville_livraison,
                     A_FACT.nom                  AS nom_facturation,
                     A_FACT.rue                  AS rue_facturation,
                     A_FACT.code_postal          AS code_postal_facturation,
                     A_FACT.ville                AS ville_facturation,
                     IF(C.id_adresse = C.id_adresse_1,
                        'adresse_identique',
                        'adresse_non_identique') AS adresse_identique
              FROM commande C
                       JOIN adresse A_LIV ON C.id_adresse = A_LIV.id_adresse
                       JOIN adresse A_FACT ON C.id_adresse_1 = A_FACT.id_adresse
              WHERE C.id_commande = %s \
              '''
        mycursor.execute(sql, id_commande)
        commande_adresses = mycursor.fetchone()

    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , velos_commande=velos_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get', 'post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = '''
              UPDATE commande \
              SET id_etat = (SELECT etat.id_etat from etat WHERE libelle = 'expédié')
              WHERE id_commande = %s \
              '''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')