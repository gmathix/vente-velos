#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_velo = Blueprint('admin_type_velo', __name__,
                        template_folder='templates')

@admin_type_velo.route('/admin/type-velo/show')
def show_type_velo():
    mycursor = get_db().cursor()
    # sql = '''         '''
    # mycursor.execute(sql)
    # types_velo = mycursor.fetchall()
    types_velo=[]
    return render_template('admin/type_velo/show_type_velo.html', types_velo=types_velo)

@admin_type_velo.route('/admin/type-velo/add', methods=['GET'])
def add_type_velo():
    return render_template('admin/type_velo/add_type_velo.html')

@admin_type_velo.route('/admin/type-velo/add', methods=['POST'])
def valid_add_type_velo():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''         '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-velo/show') #url_for('show_type_velo')

@admin_type_velo.route('/admin/type-velo/delete', methods=['GET'])
def delete_type_velo():
    id_type_velo = request.args.get('id_type_velo', '')
    mycursor = get_db().cursor()

    flash(u'suppression type velo , id : ' + id_type_velo, 'alert-success')
    return redirect('/admin/type-velo/show')

@admin_type_velo.route('/admin/type-velo/edit', methods=['GET'])
def edit_type_velo():
    id_type_velo = request.args.get('id_type_velo', '')
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, (id_type_velo,))
    type_velo = mycursor.fetchone()
    return render_template('admin/type_velo/edit_type_velo.html', type_velo=type_velo)

@admin_type_velo.route('/admin/type-velo/edit', methods=['POST'])
def valid_edit_type_velo():
    libelle = request.form['libelle']
    id_type_velo = request.form.get('id_type_velo', '')
    tuple_update = (libelle, id_type_velo)
    mycursor = get_db().cursor()
    sql = '''   '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'type velo modifié, id: ' + id_type_velo + " libelle : " + libelle, 'alert-success')
    return redirect('/admin/type-velo/show')








