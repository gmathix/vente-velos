# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')


@admin_dataviz.route('/admin/dataviz/etat1')
def show_dataviz_tableau():
    mycursor = get_db().cursor()

    # Nombre de ventes et chiffre d'affaire par departement
    # Les 2 premiers chiffres du code postal = numero de departement
    # LEFT() en SQL pour extraire les 2 chiffres de gauche
    # SUM et COUNT en SQL, aucun calcul Python
    sql = '''
        SELECT LEFT(adresse.code_postal, 2)          AS departement,
               COUNT(DISTINCT commande.id_commande)  AS nb_ventes,
               SUM(ligne_commande.prix * ligne_commande.quantite) AS chiffre_affaire
        FROM commande
        JOIN adresse       ON commande.id_adresse = adresse.id_adresse
        JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
        GROUP BY LEFT(adresse.code_postal, 2)
        ORDER BY chiffre_affaire DESC
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()

    # Labels et valeurs pour les graphiques chart.js
    # Listes construites en Python a partir du fetchall, pas de calcul
    labels_dep    = [str(row['departement'])    for row in datas_show]
    values_ventes = [int(row['nb_ventes'])      for row in datas_show]
    values_ca     = [float(row['chiffre_affaire']) for row in datas_show]

    return render_template('admin/dataviz/dataviz_etat_1.html',
                           datas_show=datas_show,
                           labels_dep=labels_dep,
                           values_ventes=values_ventes,
                           values_ca=values_ca)


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()

    # choix : 'nb_ventes' ou 'chiffre_affaire', transmis par lien GET
    choix = request.args.get('choix', 'nb_ventes')

    sql = '''
        SELECT LEFT(adresse.code_postal, 2)          AS dep,
               COUNT(DISTINCT commande.id_commande)  AS nb_ventes,
               SUM(ligne_commande.prix * ligne_commande.quantite) AS chiffre_affaire
        FROM commande
        JOIN adresse        ON commande.id_adresse = adresse.id_adresse
        JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
        GROUP BY LEFT(adresse.code_postal, 2)
        ORDER BY dep ASC
    '''
    mycursor.execute(sql)
    datas = mycursor.fetchall()

    # Valeur maximale pour calculer l'indice (intensite couleur) en SQL
    sql_max = '''
        SELECT MAX(sous.valeur) AS valeur_max
        FROM (
            SELECT IF(%s = 'nb_ventes',
                      COUNT(DISTINCT commande.id_commande),
                      SUM(ligne_commande.prix * ligne_commande.quantite)
                   ) AS valeur
            FROM commande
            JOIN adresse        ON commande.id_adresse = adresse.id_adresse
            JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
            GROUP BY LEFT(adresse.code_postal, 2)
        ) AS sous
    '''
    mycursor.execute(sql_max, choix)
    valeur_max = mycursor.fetchone()['valeur_max']

    # Construction du dictionnaire dep -> indice (0.0 a 1.0) pour colorier la carte
    # L'indice est calcule en SQL via ROUND et division
    sql_indice = '''
        SELECT LEFT(adresse.code_postal, 2) AS dep,
               IF(%s = 'nb_ventes',
                  ROUND(COUNT(DISTINCT commande.id_commande) / %s, 2),
                  ROUND(SUM(ligne_commande.prix * ligne_commande.quantite) / %s, 2)
               ) AS indice,
               COUNT(DISTINCT commande.id_commande)  AS nb_ventes,
               SUM(ligne_commande.prix * ligne_commande.quantite) AS chiffre_affaire
        FROM commande
        JOIN adresse        ON commande.id_adresse = adresse.id_adresse
        JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
        GROUP BY LEFT(adresse.code_postal, 2)
    '''
    mycursor.execute(sql_indice, (choix, valeur_max, valeur_max))
    adresses = mycursor.fetchall()

    return render_template('admin/dataviz/dataviz_etat_map.html',
                           adresses=adresses,
                           choix=choix)