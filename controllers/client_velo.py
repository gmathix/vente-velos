
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session
from connexion_db import get_db

client_velo = Blueprint('client_velo', __name__, template_folder='templates')


@client_velo.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    session['filter_word']     = request.form.get('filter_word', '').strip()
    session['filter_types']    = request.form.getlist('filter_types')
    session['filter_prix_min'] = request.form.get('filter_prix_min', '').strip()
    session['filter_prix_max'] = request.form.get('filter_prix_max', '').strip()
    return redirect('/client/velo/show')


@client_velo.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_types', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    return redirect('/client/velo/show')


@client_velo.route('/client/index')
@client_velo.route('/client/velo/show')
def client_velo_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Lecture des filtres depuis la session
    filtre_types     = session.get('filter_types', [])
    filtre_recherche = session.get('filter_word', '')
    filtre_prix_min  = session.get('filter_prix_min', '')
    filtre_prix_max  = session.get('filter_prix_max', '')

    sql = '''
        SELECT nom_velo AS nom,
               velo.id_velo AS id_velo,
               velo.image AS image,
                MIN(declinaison_velo.prix_declinaison) AS prix,
                SUM(declinaison_velo.stock) AS stock,
                COUNT(declinaison_velo.id_declinaison_velo) AS nb_declinaison
        FROM velo
        INNER JOIN declinaison_velo ON velo.id_velo = declinaison_velo.id_velo
    '''
    list_param = []
    list_conditions = []

    if filtre_recherche:
        list_conditions.append('(nom_velo LIKE %s)')
        list_param.append(f'%{filtre_recherche}%')

    if filtre_types:
        placeholders = ', '.join(['%s'] * len(filtre_types))
        list_conditions.append(f'(velo.id_type_velo IN ({placeholders}))')
        list_param.extend(filtre_types)

    if filtre_prix_min:
        list_conditions.append('(prix_velo >= %s)')
        list_param.append(filtre_prix_min)

    if filtre_prix_max:
        list_conditions.append('(prix_velo <= %s)')
        list_param.append(filtre_prix_max)

    if len(list_conditions) > 0:
        sql += "\nWHERE "
        sql += ' AND '.join(list_conditions)

    sql += "GROUP BY velo.prix_velo, nom_velo, velo.id_velo, velo.image"

    mycursor.execute(sql, list_param)
    velos = mycursor.fetchall()

    # Types de vélos pour les cases à cocher
    mycursor.execute('''
        SELECT libelle_type_velo AS libelle, id_type_velo AS id_type_velo
        FROM type_velo
    ''')
    types_velo = mycursor.fetchall()

    # Panier
    sql = '''
          SELECT 
              ligne_panier.id_declinaison_velo AS id_declinaison_velo,
             velo.nom_velo AS nom,
             ligne_panier.quantite AS quantite,
             d.prix_declinaison AS prix,
             d.stock AS stock,
            d.id_couleur AS id_couleur,
            d.id_taille AS id_taille,
              taille.libelle AS libelle_taille,
              couleur.libelle AS libelle_couleur
        FROM ligne_panier
        INNER JOIN declinaison_velo d ON ligne_panier.id_declinaison_velo = d.id_declinaison_velo
        INNER JOIN velo ON d.id_velo = velo.id_velo
        INNER JOIN taille ON d.id_taille = taille.id_taille
          INNER JOIN couleur ON d.id_couleur = couleur.id_couleur
        WHERE ligne_panier.id_utilisateur = %s
        GROUP BY id_declinaison_velo, velo.id_velo, velo.nom_velo, ligne_panier.quantite, d.prix_declinaison, d.stock, d.id_couleur, d.id_taille, taille.libelle, couleur.libelle
    '''
    mycursor.execute(sql, id_client)
    velos_panier = mycursor.fetchall()

    prix_total = None
    if len(velos_panier) >= 1:
        prix_total = sum(v['prix'] * v['quantite'] for v in velos_panier)

    return render_template('client/boutique/panier_velo.html',
                           velos=velos,
                           velos_panier=velos_panier,
                           prix_total=prix_total,
                           items_filtre=types_velo,
                           )