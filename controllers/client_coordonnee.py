# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db
from datetime import datetime

client_coordonnee = Blueprint('client_coordonnee', __name__,
                        template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    sql = '''
        SELECT adresse.id_adresse,nom,rue,code_postal,ville,adresse_favorite,addresse_valide COUNT(DISTINCT commande.id_commande) AS nbr_commandes
        FROM adresse
        LEFT JOIN commande ON adresse.id_adresse = commande.id_adresse_livraison-
        OR adresse.id_adresse = commande.id_adresse_1 
        WHERE utilisateur.id_utilisateur = %s
        GROUP BY adresse.id_adresse,nom,rue,code_postal,ville,adresse_favorite,addresse_valide 
        ORDER BY  addresse_favorite DESC
    '''
    mycursor.execute(sql, id_client)
    adresses = mycursor.fetchall()
    nb_adresses = len(adresses)

    sql = '''
          SELECT COUNT(*) AS nombre_adresses_valides
          FROM adresse
          WHERE id_utilisateur = %s AND valide = TRUE 
          '''
    mycursor.execute(sql, id_client)
    nombre_adresses_valides=mycursor.fetchone()['nombres_adresses_valides']

    print(adresses)

    return render_template('client/coordonnee/show_coordonnee.html'
                           , utilisateur=utilisateur
                           , adresses=adresses
                           , nb_adresses=nb_adresses
                           , nombre_adresses_valides_adresses=nombre_adresses_valides
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_coordonnee.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom=request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    sql = ''' SELECT * \
              FROM utilisateur \
              WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    user = mycursor.fetchone()

    sql = ''' SELECT * FROM utilisateur WHERE (login = %s OR email = %s) AND id_utilisateur != %s'''
    mycursor.execute(sql, (login, email, id_client))
    utilisateur = mycursor.fetchall()

    if utilisateur:
        flash(u'votre cet Email ou ce Login existe déjà pour un autre utilisateur', 'alert-warning')
        return render_template('client/coordonnee/edit_coordonnee.html'
                               , utilisateur=user
                               )

    sql = ''' UPDATE utilisateur SET 
        login = %s, nom = %s, email = %s WHERE id_utilisateur = %s
          '''
    mycursor.execute(sql, (login, nom, email, id_client))

    get_db().commit()
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse',methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse= request.form.get('id_adresse')

    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''SELECT * FROM utilisateur WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html',
                           utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/add_adresse',methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    sql = '''
    INSERT INTO adresse (nom, rue, code_postal, ville, date_utilisation, id_utilisateur) VALUES 
        (%s, %s, %s, %s, %s, %s)
    '''
    mycursor.execute(sql, (nom, rue, code_postal, ville, datetime.now(), id_client))
    get_db().commit()

    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')

    return render_template('/client/coordonnee/edit_adresse.html'
                           # ,utilisateur=utilisateur
                           # ,adresse=adresse
                           )

@client_coordonnee.route('/client/coordonnee/edit_adresse',methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')

    return redirect('/client/coordonnee/show')
