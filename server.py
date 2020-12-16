#!/usr/bin/python3
from flask import Flask, render_template, url_for, request
import os
import mysql.connector
import socket
import sys
from os import path

tuxmlDB = None

if(path.exists("tunnel")):
    print("Connexion à la BDD en passant par le serveur web (SSH)")
    tuxmlDB = mysql.connector.connect(
    host='localhost',
    port=20000,
    user='web',
    password='df54ZR459',
    database='IrmaDB_result')
else:
    print("Connexion directe à la BDD")
    tuxmlDB = mysql.connector.connect(
    host='148.60.11.195',
    user='web',
    password='df54ZR459',
    database='IrmaDB_result')
print("Connecté !")

app = Flask(__name__, template_folder=os.path.abspath('templates'))


@app.route('/')
def hello_world():
    mycursor = tuxmlDB.cursor()
    mycursor.execute("SELECT COUNT(*) FROM compilations")
    nbcompil = mycursor.fetchone()[0]

    return render_template('base.html', count=nbcompil)



@app.route('/stats/')
def stats():
    cursor = tuxmlDB.cursor()
    cursor.execute("SELECT COUNT(compiled_kernel_size) FROM compilations WHERE compiled_kernel_size < 0")
    nbcompilfailed = cursor.fetchone()[0]
    cursor.execute("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version ASC")
    versions = cursor.fetchall()

    return render_template('stats.html', nbcompilfailed=nbcompilfailed, versions=versions)


@app.route('/stats/2/')
def statslaversion():
    cursor = tuxmlDB.cursor(buffered=True)
    laversion = request.args.get('laversion')
    cursor.execute("SELECT COUNT(compiled_kernel_size) FROM compilations WHERE compiled_kernel_size < 0 AND compiled_kernel_version = '{}';".format(laversion))
    versionreq = cursor.fetchall()
    cursor.execute("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version ASC")
    versions = cursor.fetchall()
    
    return render_template('statsversion.html', laversion=laversion, versionreq=versionreq, versions=versions)

@app.route('/test1')
def hello():
    path = request.path
    method = request.method
    domain = request.base_url

    return 'path : ' + path + ' method : ' + method + 'domain' + domain


if __name__ == "__main__":
    from waitress import serve
    arg = 8000
    if len(sys.argv) == 2:
            arg = str(sys.argv[1])
    app.debug = True
    serve(app, host="127.0.0.1", port=arg)
    
