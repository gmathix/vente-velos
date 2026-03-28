
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session


from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_velo = request.form.get('id_velo')
    quantite = request.form.get('quantite')
    # ---------
    id_declinaison_velo=request.form.get('id_declinaison_velo',None)

    #ajout dans le panier d'une déclinaison d'un velo (si 1 declinaison : immédiat sinon => vu pour faire un choix)

    if id_declinaison_velo is None: # vient du catalogue
        sql = '''
            SELECT
                d.id_declinaison_velo AS id_declinaison_velo,
                d.stock AS stock,
                d.id_taille AS id_taille,
                d.id_couleur AS id_couleur,
                couleur.libelle AS libelle_couleur,
                taille.libelle AS libelle_taille
            FROM velo
            INNER JOIN declinaison_velo d ON velo.id_velo = d.id_velo
            INNER JOIN couleur ON d.id_couleur = couleur.id_couleur
            INNER JOIN taille  ON d.id_taille = taille.id_taille
            WHERE velo.id_velo = %s AND d.utilisable = TRUE
        '''
        mycursor.execute(sql, id_velo)
        declinaisons = mycursor.fetchall()
        if len(declinaisons) == 1:
            id_declinaison_velo = declinaisons[0]['id_declinaison_velo']
        elif len(declinaisons) == 0:
            abort("pb nb de declinaison")
        else:
            sql = '''
                SELECT id_velo AS id_velo,
                    nom_velo AS nom,
                    image AS image,
                    prix_velo AS prix
                FROM velo
                WHERE id_velo = %s
            '''
            mycursor.execute(sql, (id_velo))
            velo = mycursor.fetchone()
            return render_template('client/boutique/declinaison_velo.html'
                                       , declinaisons=declinaisons
                                       , quantite=quantite
                                       , velo=velo)

# ajout dans le panier d'un velo]

    sql = "SELECT * FROM ligne_panier WHERE id_declinaison_velo = %s AND id_utilisateur = %s"
    mycursor.execute(sql, (id_declinaison_velo, id_client))
    article_panier = mycursor.fetchone()

    mycursor.execute("SELECT * FROM declinaison_velo WHERE id_declinaison_velo = %s", (id_declinaison_velo))
    declinaison_velo = mycursor.fetchone()



    if not (article_panier is None) and article_panier['quantite'] >= 1:
        sql = '''
        UPDATE ligne_panier SET quantite = quantite + %s
            WHERE id_utilisateur = %s AND id_declinaison_velo = %s
        '''
        mycursor.execute(sql, (quantite, id_client, id_declinaison_velo))
    else:
        if int(quantite) >= 1:
            sql = '''
            INSERT INTO ligne_panier(id_declinaison_velo, id_utilisateur, quantite, date_ajout) 
                  VALUES(%s, %s, %s, current_timestamp)
            '''
            mycursor.execute(sql, (id_declinaison_velo, id_client, quantite))


    if declinaison_velo['stock'] >= int(quantite):
        sql = '''
        UPDATE declinaison_velo SET stock = stock - %s 
            WHERE id_declinaison_velo = %s
        '''
        mycursor.execute(sql, (quantite, id_declinaison_velo))
    else:
        flash('Stock insuffisant')
        sql = '''
        UPDATE declinaison_velo SET stock = 0 WHERE id_velo = %s
        '''
        mycursor.execute(sql, (id_declinaison_velo))


    get_db().commit()


    return redirect('/client/velo/show')

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_velo = request.form.get('id_declinaison_velo','')
    quantite = 1

    # ---------
    # partie 2 : on supprime une déclinaison de l'velo
    # id_declinaison_velo = request.form.get('id_declinaison_velo', None)

    sql = '''SELECT * FROM ligne_panier WHERE id_utilisateur=%s AND id_declinaison_velo=%s'''
    mycursor.execute(sql, (id_client, id_declinaison_velo))
    velo_panier=mycursor.fetchone()

    if not(velo_panier is None) and velo_panier['quantite'] > 1:
        sql = '''UPDATE ligne_panier SET quantite=quantite-%s 
              WHERE id_utilisateur = %s AND id_declinaison_velo = %s'''
        mycursor.execute(sql, (quantite, id_client, id_declinaison_velo))
    else:
        sql = '''DELETE FROM ligne_panier WHERE id_utilisateur = %s AND id_declinaison_velo = %s'''
        mycursor.execute(sql, (id_client, id_declinaison_velo))

    # mise à jour du stock de l'velo disponible
    get_db().commit()

    mycursor.execute("UPDATE declinaison_velo SET stock = stock + %s WHERE id_declinaison_velo = %s", (quantite, id_declinaison_velo))
    get_db().commit()

    return redirect('/client/velo/show')





@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    sql = ''' SELECT * FROM ligne_panier WHERE id_utilisateur = %s'''
    mycursor.execute(sql, (client_id))
    items_panier = mycursor.fetchall()
    for item in items_panier:
        print(item)
        sql = ''' DELETE FROM ligne_panier WHERE id_declinaison_velo = %s AND id_utilisateur = %s '''
        mycursor.execute(sql, (item['id_declinaison_velo'], client_id))
        sql2=''' UPDATE declinaison_velo SET stock = stock + %s WHERE id_declinaison_velo = %s'''
        mycursor.execute(sql2, (item['quantite'], item['id_declinaison_velo']))
        get_db().commit()
    return redirect('/client/velo/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_velo = request.form.get("id_declinaison_velo")
    #id_declinaison_velo = request.form.get('id_declinaison_velo')

    sql = ''' SELECT * FROM ligne_panier WHERE id_declinaison_velo = %s AND id_utilisateur = %s'''
    mycursor.execute(sql, (id_declinaison_velo, id_client))
    ligne = mycursor.fetchone()

    sql = ''' DELETE FROM ligne_panier WHERE id_declinaison_velo = %s AND id_utilisateur = %s '''
    mycursor.execute(sql, (id_declinaison_velo, id_client))

    sql2=''' UPDATE declinaison_velo SET stock = stock + %s WHERE id_declinaison_velo = %s'''
    mycursor.execute(sql2, (ligne['quantite'], ligne['id_declinaison_velo']))

    get_db().commit()
    return redirect('/client/velo/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types', None)
    # test des variables puis
    # mise en session des variables
    return redirect('/client/velo/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    # suppression  des variables en session
    print("suppr filtre")
    return redirect('/client/velo/show')
