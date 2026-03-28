
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
        SELECT  V.nom_velo                                AS nom,
                V.id_velo                                 AS id_velo,
                V.image                                   AS image,
                V.utilisable                              AS utilisable,
                COALESCE(MIN(D.prix_declinaison), 0)      AS prix,
                SUM(D.stock)                              AS stock,
                COUNT(D.id_declinaison_velo)              AS nb_declinaison
            
        FROM velo AS V
            
        LEFT JOIN declinaison_velo D ON V.id_velo = D.id_velo
            
        WHERE D.utilisable = TRUE AND V.utilisable = TRUE

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

    sql += "GROUP BY V.prix_velo, V.nom_velo, V.id_velo, V.image, V.utilisable"

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
                L.id_declinaison_velo AS id_declinaison_velo,
                L.quantite            AS quantite,
                V.nom_velo            AS nom,
                D.prix_declinaison    AS prix,
                D.stock               AS stock,
                D.id_couleur          AS id_couleur,
                D.id_taille           AS id_taille,
                T.libelle             AS libelle_taille,
                C.libelle             AS libelle_couleur
            
        FROM ligne_panier AS L
            
        JOIN declinaison_velo D ON L.id_declinaison_velo = D.id_declinaison_velo
        JOIN velo V ON D.id_velo = V.id_velo
        JOIN taille T ON D.id_taille = T.id_taille
        JOIN couleur C ON D.id_couleur = C.id_couleur
            
        WHERE L.id_utilisateur = %s 
            
        GROUP BY id_declinaison_velo, V.id_velo, V.nom_velo, L.quantite, D.prix_declinaison, D.stock, D.id_couleur, D.id_taille, T.libelle, C.libelle
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