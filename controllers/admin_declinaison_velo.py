
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


    sql = '''
        SELECT * 
        FROM velo
        
        WHERE id_velo = %s
    '''
    mycursor.execute(sql, id_velo)
    velo = mycursor.fetchone()


    sql = '''
        SELECT *
        FROM couleur
    '''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()

    sql = '''
          SELECT *
          FROM taille
          '''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()

    d_taille_uniq = len(tailles) == 1
    d_couleur_uniq = len(couleurs) == 1

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


    sql = '''
        SELECT id_taille, id_couleur
        FROM declinaison_velo
        WHERE id_velo = %s AND id_taille = %s AND id_couleur = %s
    '''
    mycursor.execute(sql, (id_velo, taille, couleur))
    declinaisons = mycursor.fetchall()
    if len(declinaisons) >= 1: # doublon
        return redirect('/admin/velo/edit?id_velo=' + id_velo)



    sql = '''
        INSERT INTO declinaison_velo(id_velo, stock, prix_declinaison, image, id_couleur, id_taille) VALUES 
            (%s, %s, 
             (SELECT prix_velo FROM velo WHERE velo.id_velo = %s), 
             (SELECT image FROM velo WHERE velo.id_velo = %s),
             %s, %s)
    '''
    mycursor.execute(sql, (id_velo, stock, id_velo, id_velo, couleur, taille))
    get_db().commit()


    return redirect('/admin/velo/edit?id_velo=' + id_velo)


@admin_declinaison_velo.route('/admin/declinaison_velo/edit', methods=['GET'])
def edit_declinaison_velo():
    id_declinaison_velo = request.args.get('id_declinaison_velo')
    mycursor = get_db().cursor()



    sql = '''
        SELECT D.id_declinaison_velo,
               D.id_velo AS velo_id,
               D.stock AS stock,
               D.id_couleur AS couleur_id,
               D.id_taille AS taille_id,
            
               V.image AS image_velo
            
        FROM declinaison_velo AS D
            
        INNER JOIN velo V ON D.id_velo = V.id_velo
            
        WHERE D.id_declinaison_velo = %s
    '''
    mycursor.execute(sql, id_declinaison_velo)
    declinaison_velo = mycursor.fetchone()



    sql = '''
          SELECT *
          FROM couleur \
          '''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()

    sql = '''
          SELECT *
          FROM taille \
          '''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()

    d_taille_uniq = len(tailles) == 1
    d_couleur_uniq = len(couleurs) == 1
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



    # verifier qu'il y a bien un changement
    sql = '''
        SELECT 
            IF(D.id_taille = %s AND D.id_couleur = %s, 'declinaison_identique', 'declinaison_non_identique') AS declinaison_identique
        FROM declinaison_velo AS D 
        WHERE id_declinaison_velo = %s
    '''
    mycursor.execute(sql, (taille_id, couleur_id, id_declinaison_velo))

    if mycursor.fetchone()['declinaison_identique'] == 'declinaison_identique':
        flash('pas de modification', 'alert-success')
        return redirect('/admin/velo/edit?id_velo=' + str(id_velo))


    sql = '''
          SELECT COUNT(LP.id_declinaison_velo) + COUNT(LC.id_declinaison_velo) AS nombre_utilisations
          FROM declinaison_velo D
                   LEFT JOIN ligne_panier LP ON D.id_declinaison_velo = LP.id_declinaison_velo
                   LEFT JOIN ligne_commande LC ON D.id_declinaison_velo = LC.id_declinaison_velo
          WHERE D.id_declinaison_velo = %s 
    '''
    mycursor.execute(sql, id_declinaison_velo)
    nbr_utilisations = mycursor.fetchone()['nombre_utilisations']


    if nbr_utilisations > 0:
        # rendre l'ancienne inutilisable
        sql = '''
              UPDATE declinaison_velo 
              SET utilisable = FALSE
              WHERE id_declinaison_velo = %s 
              '''
        mycursor.execute(sql, id_declinaison_velo)


        # creer une nouvelle avec les memes valeurs
        sql = '''
            INSERT INTO declinaison_velo (stock, prix_declinaison, image, id_couleur, id_taille, id_velo) 
                SELECT stock, prix_declinaison, image, id_couleur, id_taille, id_velo FROM declinaison_velo WHERE id_declinaison_velo = %s
        '''
        mycursor.execute(sql, id_declinaison_velo)
        get_db().commit()

        mycursor.execute('SELECT last_insert_id();')
        new_id = mycursor.fetchone()['last_insert_id()']


        # la modifier
        sql = '''
              UPDATE declinaison_velo 
              SET stock      = %s, 
                  id_couleur = %s, 
                  id_taille  = %s 
              WHERE id_declinaison_velo = %s; 
              '''
        mycursor.execute(sql, (stock, couleur_id, taille_id, new_id))

        get_db().commit()


        flash(f'creation d\'une copie de la declinaison', 'alert-success')


    else:
        sql = '''
            UPDATE declinaison_velo SET stock = %s, id_couleur = %s, id_taille = %s WHERE id_declinaison_velo = %s;
        '''
        mycursor.execute(sql, (stock, couleur_id, taille_id, id_declinaison_velo))

        get_db().commit()



    message = u'declinaison_velo modifié , id:' + str(id_declinaison_velo) + '- stock :' + str(stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/velo/edit?id_velo=' + str(id_velo))


@admin_declinaison_velo.route('/admin/declinaison_velo/delete', methods=['GET'])
def admin_delete_declinaison_velo():
    id_declinaison_velo = request.args.get('id_declinaison_velo','')
    id_velo = request.args.get('id_velo','')
    mycursor = get_db().cursor()


    sql = '''
        SELECT COUNT(LP.id_declinaison_velo) + COUNT(LC.id_declinaison_velo) AS nombre_utilisations
        FROM declinaison_velo D
        LEFT JOIN ligne_panier LP ON D.id_declinaison_velo = LP.id_declinaison_velo
        LEFT JOIN ligne_commande LC ON D.id_declinaison_velo = LC.id_declinaison_velo
        WHERE D.id_declinaison_velo = %s
    '''
    mycursor.execute(sql, id_declinaison_velo)
    nbr_utilisations = mycursor.fetchone()['nombre_utilisations']

    if nbr_utilisations > 0:
        # declinaision devient inutilisable
        sql = '''
            UPDATE declinaison_velo SET utilisable = FALSE 
                WHERE id_declinaison_velo = %s
        '''
        mycursor.execute(sql, id_declinaison_velo)
        get_db().commit()

        flash(f'declinaison rendue non-utilisable, id_declinaison_velo : {str(id_declinaison_velo)}, nbr_utilisations : {nbr_utilisations}' , 'alert-success')
    else:
        # on peut juste la supprimer
        sql = '''
            DELETE FROM declinaison_velo WHERE id_declinaison_velo = %s
        '''
        mycursor.execute(sql, id_declinaison_velo)
        get_db().commit()

        flash(u'declinaison supprimée, id_declinaison_velo : ' + str(id_declinaison_velo), 'alert-success')



    return redirect('/admin/velo/edit?id_velo=' + str(id_velo))
