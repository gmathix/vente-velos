
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
     SELECT V.nom_velo AS nom,
            V.id_velo AS id_velo,
            V.id_type_velo AS type_velo_id,
            V.prix_velo AS prix,
            V.utilisable AS utilisable,
            COALESCE(V.image, 'pas d\\'image') AS image,
            T.libelle_type_velo AS libelle_type_velo,
            SUM(D.stock) AS stock,
            MIN(D.stock) AS min_stock,
            COUNT(D.id_declinaison_velo) AS nb_declinaisons
            
     FROM velo AS V
         
     JOIN type_velo T ON V.id_type_velo = T.id_type_velo
     LEFT JOIN declinaison_velo D ON V.id_velo = D.id_velo
         
     GROUP BY V.id_velo, V.nom_velo, V.utilisable, V.id_type_velo, V.prix_velo, V.image, T.libelle_type_velo
         
     ORDER BY V.nom_velo ASC
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
    image = request.files.get('image', '')


    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    tuple_add = (None, nom,  prix, description, filename,type_velo_id)

    sql = '''
    INSERT INTO velo (id_velo, nom_velo, prix_velo, description, image, id_type_velo) VALUES
          (%s, %s, %s, %s, %s, %s)'''

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


    sql = '''SELECT COUNT(D.id_declinaison_velo) AS nb_declinaison
          FROM velo 
          INNER JOIN declinaison_velo D ON velo.id_velo = D.id_velo
         WHERE velo.id_velo = %s AND D.utilisable = TRUE
          '''
    mycursor.execute(sql, id_velo)
    nb_declinaison = mycursor.fetchone()


    if nb_declinaison and nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet velo : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        # verifier l'utilisation du velo
        sql = '''
            SELECT COUNT(*) AS nbr_utilisations
                
            FROM velo 
            JOIN note        N ON velo.id_velo = N.id_velo
            JOIN commentaire C ON velo.id_velo = C.id_velo
            JOIN liste_envie L ON velo.id_velo = L.id_velo
            JOIN historique  H ON velo.id_velo = H.id_velo
            LEFT JOIN declinaison_velo D ON velo.id_velo = D.id_velo
                
                
            WHERE velo.id_velo = %s
        '''
        mycursor.execute(sql, id_velo)
        nbr_utilisations = mycursor.fetchone()['nbr_utilisations']

        if int(nbr_utilisations) >= 1:
            sql = '''
                UPDATE velo SET utilisable = FALSE
                    WHERE id_velo = %s
            '''
            mycursor.execute(sql, id_velo)
            get_db().commit()

        else:
            sql = ''' SELECT image AS image FROM velo WHERE id_velo = %s'''
            mycursor.execute(sql, id_velo)
            velo = mycursor.fetchone()
            image = velo['image']


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

    sql = '''
          SELECT COUNT(D.id_declinaison_velo) AS nb_declinaison
          FROM velo 
          INNER JOIN declinaison_velo D ON velo.id_velo = D.id_velo
         WHERE velo.id_velo = %s
     '''
    mycursor.execute(sql, id_velo)
    nb_declinaison = mycursor.fetchone()

    if nb_declinaison and nb_declinaison['nb_declinaison'] > 0:
        message = u'il y a des declinaisons dans cet velo : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' SELECT image AS image \
                  FROM velo \
                  WHERE id_velo = %s'''
        mycursor.execute(sql, id_velo)
        velo = mycursor.fetchone()
        image = velo['image']

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
        SELECT V.nom_velo                   AS nom,
               V.description                AS description,
               V.id_velo                    AS id_velo,
               V.id_type_velo               AS type_velo_id,
               V.prix_velo                  AS prix,
               V.image                      AS image,
               T.libelle_type_velo          AS libelle_type_velo,
               SUM(D.stock)                 AS stock,
               MIN(D.stock)                 AS min_stock,
               COUNT(D.id_declinaison_velo) AS nb_declinaisons
        
        FROM velo AS V
            
        JOIN type_velo T ON V.id_type_velo = T.id_type_velo
        LEFT JOIN declinaison_velo D ON V.id_velo = D.id_velo
            
        WHERE V.id_velo = %s
            
        GROUP BY V.id_velo, V.nom_velo, V.description, V.id_type_velo, V.prix_velo, V.image, T.libelle_type_velo
        
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

    sql = '''
        SELECT D.id_velo             AS velo_id,
               D.id_declinaison_velo AS id_declinaison_velo,
               D.id_taille           AS id_taille,
               D.id_couleur          AS id_couleur,
               D.stock               AS stock,
               D.utilisable          AS utilisable,
               C.libelle             AS libelle_couleur,
               T.libelle             AS libelle_taille
            
        FROM declinaison_velo as D
            
        JOIN couleur C ON D.id_couleur = C.id_couleur
        JOIN taille T ON D.id_taille = T.id_taille
            
        WHERE D.id_velo = %s
            
        ORDER BY D.utilisable DESC
    '''
    mycursor.execute(sql, id_velo)
    declinaisons_velo = mycursor.fetchall()

    return render_template('admin/velo/edit_velo.html'
                           ,velo=velo
                           ,types_velo=types_velo
                           ,declinaisons_velo=declinaisons_velo
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

    sql = ''' SELECT image AS image FROM velo WHERE id_velo = %s'''
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
    sql = '''  UPDATE velo SET nom_velo = %s, image = %s, prix_velo = %s, velo.id_type_velo = %s, description = %s WHERE id_velo = %s '''
    mycursor.execute(sql, (nom, image_nom, prix, type_velo_id, description, id_velo))



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
