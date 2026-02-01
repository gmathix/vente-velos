#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_velo = Blueprint('admin_declinaison_velo', __name__,
                         template_folder='templates')


@admin_declinaison_velo.route('/admin/declinaison_velo/add')
def add_declinaison_velo():
    id_velo=request.args.get('id_velo')
    mycursor = get_db().cursor()
    velo=[]
    couleurs=None
    tailles=None
    d_taille_uniq=None
    d_couleur_uniq=None
    return render_template('admin/velo/add_declinaison_velo.html'
                           , velo=velo
                           , couleurs=couleurs
                           , tailles=tailles
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_velo.route('/admin/declinaison_velo/add', methods=['POST'])
def valid_add_declinaison_velo():
    mycursor = get_db().cursor()

    id_velo = request.form.get('id_velo')
    stock = request.form.get('stock')
    taille = request.form.get('taille')
    couleur = request.form.get('couleur')
    # attention au doublon
    get_db().commit()
    return redirect('/admin/velo/edit?id_velo=' + id_velo)


@admin_declinaison_velo.route('/admin/declinaison_velo/edit', methods=['GET'])
def edit_declinaison_velo():
    id_declinaison_velo = request.args.get('id_declinaison_velo')
    mycursor = get_db().cursor()
    declinaison_velo=[]
    couleurs=None
    tailles=None
    d_taille_uniq=None
    d_couleur_uniq=None
    return render_template('admin/velo/edit_declinaison_velo.html'
                           , tailles=tailles
                           , couleurs=couleurs
                           , declinaison_velo=declinaison_velo
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_velo.route('/admin/declinaison_velo/edit', methods=['POST'])
def valid_edit_declinaison_velo():
    id_declinaison_velo = request.form.get('id_declinaison_velo','')
    id_velo = request.form.get('id_velo','')
    stock = request.form.get('stock','')
    taille_id = request.form.get('id_taille','')
    couleur_id = request.form.get('id_couleur','')
    mycursor = get_db().cursor()

    message = u'declinaison_velo modifié , id:' + str(id_declinaison_velo) + '- stock :' + str(stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/velo/edit?id_velo=' + str(id_velo))


@admin_declinaison_velo.route('/admin/declinaison_velo/delete', methods=['GET'])
def admin_delete_declinaison_velo():
    id_declinaison_velo = request.args.get('id_declinaison_velo','')
    id_velo = request.args.get('id_velo','')

    flash(u'declinaison supprimée, id_declinaison_velo : ' + str(id_declinaison_velo),  'alert-success')
    return redirect('/admin/velo/edit?id_velo=' + str(id_velo))
