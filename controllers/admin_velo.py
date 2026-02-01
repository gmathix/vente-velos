#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
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
    sql = '''  requête admin_velo_1
    '''
    mycursor.execute(sql)
    velos = mycursor.fetchall()
    return render_template('admin/velo/show_velo.html', velos=velos)


@admin_velo.route('/admin/velo/add', methods=['GET'])
def add_velo():
    mycursor = get_db().cursor()

    return render_template('admin/velo/add_velo.html'
                           #,types_velo=type_velo,
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

    sql = '''  requête admin_velo_2 '''

    tuple_add = (nom, filename, prix, type_velo_id, description)
    print(tuple_add)
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
    sql = ''' requête admin_velo_3 '''
    mycursor.execute(sql, id_velo)
    nb_declinaison = mycursor.fetchone()
    if nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet velo : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' requête admin_velo_4 '''
        mycursor.execute(sql, id_velo)
        velo = mycursor.fetchone()
        print(velo)
        image = velo['image']

        sql = ''' requête admin_velo_5  '''
        mycursor.execute(sql, id_velo)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un velo supprimé, id :", id_velo)
        message = u'un velo supprimé, id : ' + id_velo
        flash(message, 'alert-success')

    return redirect('/admin/velo/show')


@admin_velo.route('/admin/velo/edit', methods=['GET'])
def edit_velo():
    id_velo=request.args.get('id_velo')
    mycursor = get_db().cursor()
    sql = '''
    requête admin_velo_6    
    '''
    mycursor.execute(sql, id_velo)
    velo = mycursor.fetchone()
    print(velo)
    sql = '''
    requête admin_velo_7
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
    sql = '''
       requête admin_velo_8
       '''
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

    sql = '''  requête admin_velo_9 '''
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
