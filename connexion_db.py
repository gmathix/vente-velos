from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

import pymysql.cursors
import os
from dotenv import load_dotenv
load_dotenv()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(
            host=os.environ.get('HOST'),
            user=os.environ.get('LOGIN'),
            password=os.environ.get('PASSWORD'),
            database=os.environ.get('DATABASE'),
            port=int(os.environ.get("DB_PORT", 3306)),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # à activer sur les machines personnelles :
        activate_db_options(db)
    return db

def activate_db_options(db):
    cursor = db.cursor()
    # Vérifier et activer l'option ONLY_FULL_GROUP_BY si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            print('MYSQL : il manque le mode ONLY_FULL_GROUP_BY')   # mettre en commentaire
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
        else:
            print('MYSQL : mode ONLY_FULL_GROUP_BY  ok')   # mettre en commentaire

def activate_db_options(db):
    cursor = db.cursor()

    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()

    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()

    cursor.close()