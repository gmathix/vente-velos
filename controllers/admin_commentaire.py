#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                        template_folder='templates')


@admin_commentaire.route('/admin/velo/commentaires', methods=['GET'])
def admin_velo_details():
    mycursor = get_db().cursor()
    id_velo =  request.args.get('id_velo', None)
    sql = '''    requête admin_type_velo_1    '''
    commentaires = {}
    sql = '''   requête admin_type_velo_1_bis   '''
    velo = []
    sql = '''   requête admin_type_velo_1_3   '''
    nb_commentaires = []
    return render_template('admin/velo/show_velo_commentaires.html'
                           , commentaires=commentaires
                           , velo=velo
                           , nb_commentaires=nb_commentaires
                           )

@admin_commentaire.route('/admin/velo/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_utilisateur = request.form.get('id_utilisateur', None)
    id_velo = request.form.get('id_velo', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''    requête admin_type_velo_2   '''
    tuple_delete=(id_utilisateur,id_velo,date_publication)
    get_db().commit()
    return redirect('/admin/velo/commentaires?id_velo='+id_velo)


@admin_commentaire.route('/admin/velo/commentaires/repondre', methods=['POST','GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_utilisateur = request.args.get('id_utilisateur', None)
        id_velo = request.args.get('id_velo', None)
        date_publication = request.args.get('date_publication', None)
        return render_template('admin/velo/add_commentaire.html',id_utilisateur=id_utilisateur,id_velo=id_velo,date_publication=date_publication )

    mycursor = get_db().cursor()
    id_utilisateur = session['id_user']   #1 admin
    id_velo = request.form.get('id_velo', None)
    date_publication = request.form.get('date_publication', None)
    commentaire = request.form.get('commentaire', None)
    sql = '''    requête admin_type_velo_3   '''
    get_db().commit()
    return redirect('/admin/velo/commentaires?id_velo='+id_velo)


@admin_commentaire.route('/admin/velo/commentaires/valider', methods=['POST','GET'])
def admin_comment_valider():
    id_velo = request.args.get('id_velo', None)
    mycursor = get_db().cursor()
    sql = '''   requête admin_type_velo_4   '''
    get_db().commit()
    return redirect('/admin/velo/commentaires?id_velo='+id_velo)