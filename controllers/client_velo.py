
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

    # Construction du SQL avec filtres dynamiques
    sql = '''
        SELECT nom_velo AS nom,
               prix_velo AS prix,
               id_velo AS id_velo,
               photo AS image,
               stock AS stock,
               libelle_taille AS libelle_taille
        FROM velo
        INNER JOIN taille ON velo.id_taille = taille.id_taille
        WHERE 1=1
    '''
    list_param = []

    if filtre_recherche:
        sql += ' AND nom_velo LIKE %s'
        list_param.append(f'%{filtre_recherche}%')

    if filtre_types:
        placeholders = ', '.join(['%s'] * len(filtre_types))
        sql += f' AND velo.id_type_velo IN ({placeholders})'
        list_param.extend(filtre_types)

    if filtre_prix_min:
        sql += ' AND prix_velo >= %s'
        list_param.append(filtre_prix_min)

    if filtre_prix_max:
        sql += ' AND prix_velo <= %s'
        list_param.append(filtre_prix_max)

    mycursor.execute(sql, list_param)
    velos = mycursor.fetchall()

    # Types de vélos pour les cases à cocher
    mycursor.execute('''
        SELECT libelle_type_velo AS libelle, id_type_velo AS id_type_velo
        FROM type_velo
    ''')
    types_velo = mycursor.fetchall()

    # Panier
    mycursor.execute('''
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
    ''', [id_client])
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