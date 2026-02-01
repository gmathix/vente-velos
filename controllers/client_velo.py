#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_velo = Blueprint('client_velo', __name__,
                        template_folder='templates')

@client_velo.route('/client/index')
@client_velo.route('/client/velo/show')              # remplace /client
def client_velo_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
    SELECT nom_velo AS nom,
            prix_velo AS prix,
            id_velo AS velo_id,
            photo AS image,
            stock AS stock
    FROM velo
    '''
    list_param = []
    condition_and = ""
    mycursor.execute(sql, list_param)

    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    velos = mycursor.fetchall()


    # pour le filtre
    types_velo = []
    sql = '''
    SELECT libelle_type_velo AS libelle, id_type_velo AS id_type_velo
    FROM type_velo;
    '''
    mycursor.execute(sql)
    types_velo = mycursor.fetchall()



    velos_panier = []

    if len(velos_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    return render_template('client/boutique/panier_velo.html'
                           , velos=velos
                           , velos_panier=velos_panier
                           #, prix_total=prix_total
                           , items_filtre=types_velo
                           )
