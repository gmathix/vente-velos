# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')


@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_velo_stock():
    mycursor = get_db().cursor()
    sql = '''
          SELECT TV.libelle_type_velo AS libelle,
                 TV.id_type_velo      AS id_type_velo,
                 COUNT(V.id_velo)     AS nbr_velos

          FROM type_velo AS TV

                   INNER JOIN velo V ON TV.id_type_velo = V.id_type_velo

          GROUP BY TV.libelle_type_velo, TV.id_type_velo \
          '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()
    labels = [str(row['libelle']) for row in datas_show]
    values = [int(row['nbr_velos']) for row in datas_show]

    sql = '''
          SELECT COUNT(*) AS nbr_velos
          FROM velo \
          '''
    mycursor.execute(sql)
    cout_total = mycursor.fetchone()


    # stock total par couleur
    sql = '''
          SELECT C.libelle                          AS libelle_couleur,
                 CONCAT('#', LPAD(HEX(C.code_couleur), 6, '0')) AS hex_couleur,
                 COUNT(DV.id_declinaison_velo)      AS nbr_declinaisons,
                 SUM(DV.stock)                      AS stock_total
          FROM couleur C
          INNER JOIN declinaison_velo DV ON C.id_couleur = DV.id_couleur
          GROUP BY C.id_couleur, C.libelle, C.code_couleur
          ORDER BY stock_total DESC
          '''
    mycursor.execute(sql)
    datas_couleur = mycursor.fetchall()
    labels_couleur = [str(row['libelle_couleur']) for row in datas_couleur]
    values_couleur = [int(row['stock_total']) for row in datas_couleur]
    hex_couleurs = [str(row['hex_couleur']) for row in datas_couleur]


    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , cout_total=cout_total
                           , datas_show=datas_show
                           , labels=labels
                           , values=values
                           , labels_couleur=labels_couleur
                           , values_couleur=values_couleur
                           , hex_couleurs=hex_couleurs)


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