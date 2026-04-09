# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session

from connexion_db import get_db

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
        SELECT adresse.id_adresse,
               adresse.nom,
               adresse.rue,
               adresse.code_postal,
               adresse.ville,
               adresse.valide,
               adresse.favori,
               COUNT(DISTINCT commande.id_commande) AS nbr_commandes
        FROM adresse
        LEFT JOIN commande ON adresse.id_adresse = commande.id_adresse
                           OR adresse.id_adresse = commande.id_adresse_1
        WHERE adresse.id_utilisateur = %s
        GROUP BY adresse.id_adresse, adresse.nom, adresse.rue,
                 adresse.code_postal, adresse.ville, adresse.valide, adresse.favori
        ORDER BY adresse.favori DESC, adresse.date_utilisation DESC
    '''
    mycursor.execute(sql, id_client)
    adresses = mycursor.fetchall()

    sql = '''
        SELECT COUNT(*) AS nb_valides
        FROM adresse
        WHERE id_utilisateur = %s AND valide = TRUE
    '''
    mycursor.execute(sql, id_client)
    nb_adresses = mycursor.fetchone()['nb_valides']

    sql = '''
        SELECT COUNT(*) AS nb_total
        FROM adresse
        WHERE id_utilisateur = %s
    '''
    mycursor.execute(sql, id_client)
    nb_adresses_tot = mycursor.fetchone()['nb_total']

    return render_template('client/coordonnee/show_coordonnee.html',
                           utilisateur=utilisateur,
                           adresses=adresses,
                           nb_adresses=nb_adresses,
                           nb_adresses_tot=nb_adresses_tot)


@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_coordonnee.html',
                           utilisateur=utilisateur)


@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom   = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    user = mycursor.fetchone()

    sql = '''
        SELECT id_utilisateur FROM utilisateur
        WHERE (login = %s OR email = %s) AND id_utilisateur != %s
    '''
    mycursor.execute(sql, (login, email, id_client))
    doublon = mycursor.fetchone()

    if doublon != None:
        flash(u'Cet email ou ce login existe deja pour un autre utilisateur.', 'alert-warning')
        return render_template('client/coordonnee/edit_coordonnee.html',
                               utilisateur=user)

    sql = '''
        UPDATE utilisateur SET login = %s, nom = %s, email = %s
        WHERE id_utilisateur = %s
    '''
    mycursor.execute(sql, (login, nom, email, id_client))
    get_db().commit()

    # Mise a jour de la session pour que la navbar reflète les nouvelles valeurs
    session['login'] = login

    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['GET'])
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html',
                           utilisateur=utilisateur)


@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client   = session['id_user']
    nom         = request.form.get('nom')
    rue         = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville       = request.form.get('ville')

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    # Verification code postal : 5 chiffres, cote serveur Python
    if len(code_postal) != 5 or code_postal.isdigit() == False:
        flash(u'Le code postal doit etre compose de 5 chiffres.', 'alert-warning')
        return render_template('client/coordonnee/add_adresse.html',
                               utilisateur=utilisateur,
                               nom=nom, rue=rue,
                               code_postal=code_postal, ville=ville)

    # Verification limite 4 adresses valides en SQL
    sql = '''
        SELECT COUNT(*) AS nb_valides
        FROM adresse
        WHERE id_utilisateur = %s AND valide = TRUE
    '''
    mycursor.execute(sql, id_client)
    nb_valides = mycursor.fetchone()['nb_valides']

    if nb_valides >= 4:
        flash(u'Maximum de 4 adresses valides atteint.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    # favori = TRUE si c'est la 1ere adresse valide, FALSE sinon
    # IF() en SQL evite un calcul Python
    sql = '''
        INSERT INTO adresse (nom, rue, code_postal, ville, date_utilisation, valide, favori, id_utilisateur)
        VALUES (%s, %s, %s, %s, NOW(), TRUE,
                IF((SELECT COUNT(*) FROM adresse a WHERE a.id_utilisateur = %s AND a.valide = TRUE) = 0,
                   TRUE, FALSE),
                %s)
    '''
    mycursor.execute(sql, (nom, rue, code_postal, ville, id_client, id_client))
    get_db().commit()
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client  = session['id_user']
    id_adresse = request.form.get('id_adresse')

    # Securite : l'adresse appartient bien au client connecte
    sql = '''
        SELECT id_adresse, favori FROM adresse
        WHERE id_adresse = %s AND id_utilisateur = %s AND valide = TRUE
    '''
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()

    if adresse == None:
        flash(u'Probleme : cette adresse ne vous appartient pas.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    # Si utilisee dans une commande : passe non valide (conservee pour historique)
    # Sinon : suppression physique
    sql = '''
        UPDATE adresse
        SET valide = FALSE, favori = FALSE
        WHERE id_adresse = %s
          AND (SELECT COUNT(*) FROM commande c
               WHERE c.id_adresse = %s OR c.id_adresse_1 = %s) > 0
    '''
    mycursor.execute(sql, (id_adresse, id_adresse, id_adresse))

    sql = '''
        DELETE FROM adresse
        WHERE id_adresse = %s
          AND (SELECT COUNT(*) FROM commande c
               WHERE c.id_adresse = %s OR c.id_adresse_1 = %s) = 0
    '''
    mycursor.execute(sql, (id_adresse, id_adresse, id_adresse))

    # Si c'etait la favorite : la derniere adresse valide utilisee en commande devient favorite
    if adresse['favori'] == 1:
        sql = '''
            UPDATE adresse
            SET favori = TRUE
            WHERE id_adresse = (
                SELECT id_adresse FROM (
                    SELECT a.id_adresse, MAX(c.date_achat) AS derniere_commande
                    FROM adresse a
                    LEFT JOIN commande c ON a.id_adresse = c.id_adresse
                                        OR a.id_adresse = c.id_adresse_1
                    WHERE a.id_utilisateur = %s AND a.valide = TRUE
                    GROUP BY a.id_adresse
                    ORDER BY derniere_commande DESC
                    LIMIT 1
                ) AS sous_requete
            )
        '''
        mycursor.execute(sql, id_client)

    get_db().commit()
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['GET'])
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client  = session['id_user']
    id_adresse = request.args.get('id_adresse')

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    # Securite : l'adresse appartient bien au client connecte
    sql = '''
        SELECT * FROM adresse
        WHERE id_adresse = %s AND id_utilisateur = %s AND valide = TRUE
    '''
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()

    if adresse == None:
        flash(u'Probleme : cette adresse ne vous appartient pas.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    return render_template('client/coordonnee/edit_adresse.html',
                           utilisateur=utilisateur,
                           adresse=adresse)


@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client   = session['id_user']
    nom         = request.form.get('nom')
    rue         = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville       = request.form.get('ville')
    id_adresse  = request.form.get('id_adresse')

    # Securite : l'adresse appartient bien au client connecte
    sql = '''
        SELECT * FROM adresse
        WHERE id_adresse = %s AND id_utilisateur = %s AND valide = TRUE
    '''
    mycursor.execute(sql, (id_adresse, id_client))
    adresse = mycursor.fetchone()

    if adresse == None:
        flash(u'Probleme : cette adresse ne vous appartient pas.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    sql = ''' SELECT * FROM utilisateur WHERE id_utilisateur = %s '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    # Verification code postal cote serveur
    if len(code_postal) != 5 or code_postal.isdigit() == False:
        flash(u'Le code postal doit etre compose de 5 chiffres.', 'alert-warning')
        return render_template('client/coordonnee/edit_adresse.html',
                               utilisateur=utilisateur,
                               adresse=adresse)

    # Si l'adresse est utilisee dans une commande :
    #   on la rend non valide et on cree une nouvelle avec les nouvelles infos
    #   la nouvelle herite du statut favori de l'ancienne
    # Sinon : simple UPDATE
    sql = '''
        SELECT COUNT(*) AS nb_commandes FROM commande
        WHERE id_adresse = %s OR id_adresse_1 = %s
    '''
    mycursor.execute(sql, (id_adresse, id_adresse))
    nb_commandes = mycursor.fetchone()['nb_commandes']

    if nb_commandes > 0:
        sql = '''
            UPDATE adresse SET valide = FALSE, favori = FALSE
            WHERE id_adresse = %s
        '''
        mycursor.execute(sql, id_adresse)

        sql = '''
            INSERT INTO adresse (nom, rue, code_postal, ville, date_utilisation, valide, favori, id_utilisateur)
            VALUES (%s, %s, %s, %s, NOW(), TRUE, %s, %s)
        '''
        mycursor.execute(sql, (nom, rue, code_postal, ville, adresse['favori'], id_client))
    else:
        sql = '''
            UPDATE adresse SET nom = %s, rue = %s, code_postal = %s, ville = %s
            WHERE id_adresse = %s
        '''
        mycursor.execute(sql, (nom, rue, code_postal, ville, id_adresse))

    get_db().commit()
    return redirect('/client/coordonnee/show')