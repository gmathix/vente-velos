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


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']

    sql = '''
        SELECT commande.id_commande AS id_commande,
                login AS login,
                date_achat AS date_achat,
                SUM(quantite) AS nbr_velos,
                SUM(ligne_commande.prix * ligne_commande.quantite) AS prix_total,
                libelle AS libelle
        FROM commande
        INNER JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
        INNER JOIN etat ON commande.id_etat = etat.id_etat
        RIGHT JOIN ligne_commande ON commande.id_commande = ligne_commande.id_commande
            GROUP BY login, date_achat, libelle, commande.id_commande
  '''
    mycursor.execute(sql)
    commandes=mycursor.fetchall()


    velos_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)


    if id_commande != None:
        sql = '''  
            SELECT utilisateur.nom AS nom,
                quantite AS quantite,
                prix AS prix,
                (quantite * prix) AS prix_ligne
                    
            FROM ligne_commande
            INNER JOIN commande ON ligne_commande.id_commande = commande.id_commande
            INNER JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
            WHERE ligne_commande.id_commande = %s  
              '''
        mycursor.execute(sql, id_commande)
        velos_commande = mycursor.fetchall()

        commande_adresses = []
    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , velos_commande=velos_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = ''' 
              UPDATE commande SET id_etat = (SELECT etat.id_etat from etat WHERE libelle = 'validé')
              WHERE id_commande = %s
          '''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')
