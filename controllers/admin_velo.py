
# -*- coding:utf-8 -*-
import math
import os.path
import math
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_velo = Blueprint('admin_velo', __name__,
                          template_folder='templates')


@admin_velo.route('/admin/velo/show')
def show_velo():
    mycursor = get_db().cursor()
    sql = ''' 
     SELECT nom_velo AS nom,
         id_velo AS id_velo,
         libelle_type_velo AS libelle_type_velo,
         velo.id_type_velo AS type_velo_id,
         libelle_taille AS libelle_taille,
         velo.id_taille AS taille_id,
         prix_velo AS prix,
         stock AS stock,
         photo AS image
     FROM velo
         INNER JOIN type_velo ON velo.id_type_velo = type_velo.id_type_velo
         INNER JOIN taille ON velo.id_taille = taille.id_taille
          '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()

    return render_template('admin/velo/show_velo.html', velos=velos)


@admin_velo.route('/admin/velo/add', methods=['GET'])
def add_velo():
    mycursor = get_db().cursor()

    sql = '''
          SELECT id_type_velo      AS id_type_velo,
                 libelle_type_velo AS libelle
          FROM type_velo \
          '''
    mycursor.execute(sql)
    types_velo = mycursor.fetchall()

    return render_template('admin/velo/add_velo.html',
                            types_velo=types_velo,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_velo.route('/admin/velo/add', methods=['POST'])
def valid_add_velo():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_velo_id = request.form.get('type_velo_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    stock = request.form.get('stock', '')
    image = request.files.get('image', '')


    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    tuple_add = (None, nom,  prix, description, filename, stock, 1, type_velo_id)

    sql = '''
    INSERT INTO velo (id_velo, nom_velo, prix_velo, description, photo, stock, id_taille, id_type_velo) VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s)'''

    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'velo ajouté , nom: ', nom, ' - type_velo:', type_velo_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'velo ajouté , nom:' + nom + '- type_velo:' + type_velo_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/velo/show')


@admin_velo.route('/admin/velo/delete', methods=['GET'])
def delete_velo():
    id_velo=request.args.get('id_velo')
    mycursor = get_db().cursor()
    sql = '''SELECT
                 0 AS nb_declinaison,
                '' AS image
             FROM velo WHERE id_velo = %s'''
    mycursor.execute(sql, id_velo)
    nb_declinaison = mycursor.fetchone()
    if nb_declinaison and nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet velo : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' SELECT photo AS image FROM velo WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)
        velo = mycursor.fetchone()
        image = velo['image']

        sql = '''DELETE FROM ligne_panier WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)

        sql = '''DELETE FROM ligne_commande WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)

        sql = ''' DELETE FROM velo WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un velo supprimé, id :", id_velo)
        message = u'un velo supprimé, id : ' + id_velo
        flash(message, 'alert-success')

    return redirect('/admin/velo/show')


@admin_velo.route('/admin/velo/delete-cascade/', methods=['GET'])
def delete_velo_cascade():
    id_velo = request.args.get('id_velo')
    id_type_velo = request.args.get('id_type_velo')
    mycursor = get_db().cursor()

    sql = '''SELECT 0  AS nb_declinaison, \
                    '' AS image
             FROM velo \
             WHERE id_velo = %s'''
    mycursor.execute(sql, id_velo)
    nb_declinaison = mycursor.fetchone()

    if nb_declinaison and nb_declinaison['nb_declinaison'] > 0:
        message = u'il y a des declinaisons dans cet velo : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' SELECT photo AS image \
                  FROM velo \
                  WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)
        velo = mycursor.fetchone()
        image = velo['image']

        sql = '''DELETE \
                 FROM ligne_panier \
                 WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)

        sql = '''DELETE \
                 FROM ligne_commande \
                 WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)

        sql = ''' DELETE \
                  FROM velo \
                  WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un velo supprimé, id :", id_velo)
        message = u'un velo supprimé, id : ' + id_velo
        flash(message, 'alert-success')

    return redirect(f'/admin/type-velo/delete?id_type_velo={id_type_velo}')


@admin_velo.route('/admin/velo/edit', methods=['GET'])
def edit_velo():
    id_velo=request.args.get('id_velo')
    mycursor = get_db().cursor()
    sql = '''
        SELECT  nom_velo AS nom,
         id_velo AS id_velo,
         id_type_velo AS type_velo_id,
         prix_velo AS prix,
         stock AS stock,
         photo AS image,
            description AS description
        FROM velo
        WHERE id_velo = %s
    '''

    mycursor.execute(sql, id_velo)
    velo = mycursor.fetchone()

    sql = '''
    SELECT id_type_velo AS id_type_velo,
          libelle_type_velo AS libelle
    FROM type_velo
    '''
    mycursor.execute(sql)
    types_velo = mycursor.fetchall()

    # sql = '''
    # requête admin_velo_6
    # '''
    # mycursor.execute(sql, id_velo)
    # declinaisons_velo = mycursor.fetchall()

    return render_template('admin/velo/edit_velo.html'
                           ,velo=velo
                           ,types_velo=types_velo
                         #  ,declinaisons_velo=declinaisons_velo
                           )


@admin_velo.route('/admin/velo/edit', methods=['POST'])
def valid_edit_velo():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_velo = request.form.get('id_velo')
    image = request.files.get('image', '')
    type_velo_id = request.form.get('type_velo_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')
    stock = request.form.get('stock')

    sql = ''' SELECT photo AS image FROM velo WHERE id_velo = %s'''
    mycursor.execute(sql, id_velo)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    print(type_velo_id)
    sql = '''  UPDATE velo SET nom_velo = %s, photo = %s, prix_velo = %s, velo.id_type_velo = %s, description = %s , stock = %s WHERE id_velo = %s '''
    mycursor.execute(sql, (nom, image_nom, prix, type_velo_id, description, stock, id_velo))


    sql = '''
        SELECT COALESCE(COUNT(ligne_panier.id_velo), 0) AS nbr_paniers, COALESCE(SUM(quantite), 0) AS nbr_velos_panier
        FROM ligne_panier
        WHERE id_velo = %s
    '''
    stock = int(stock)
    mycursor.execute(sql, id_velo)
    result = mycursor.fetchone()
    nbr_velos_panier = int(result['nbr_velos_panier'])
    nbr_paniers = int(result['nbr_paniers'])

    if stock < nbr_velos_panier:
        left = nbr_paniers - stock

        sql = '''
            SELECT quantite, id_utilisateur, id_velo
            FROM ligne_panier
            WHERE id_velo = %s
        '''
        mycursor.execute(sql, id_velo)
        paniers = mycursor.fetchmany(nbr_paniers)

        for panier in paniers:
            sub = math.ceil((panier['quantite'] / nbr_velos_panier) * left)
            sql = ''' UPDATE ligne_panier SET quantite = quantite - %s WHERE id_velo = %s AND id_utilisateur = %s '''
            mycursor.execute(sql, (sub, id_velo, panier['id_utilisateur']))
            left -= sub


    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'velo modifié , nom:' + nom + '- type_velo :' + type_velo_id + ' - prix:' + prix  + ' - image:' + image_nom + ' - description: ' + description
    flash(message, 'alert-success')
    return redirect('/admin/velo/show')







@admin_velo.route('/admin/velo/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    velo=[]
    commentaires = {}
    return render_template('admin/velo/show_avis.html'
                           , velo=velo
                           , commentaires=commentaires
                           )


@admin_velo.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    velo_id = request.form.get('idvelo', None)
    userId = request.form.get('idUser', None)

    return admin_avis(velo_id)
