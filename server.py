#!/usr/bin/python3
from flask import Flask
from flask import render_template
import os
import mysql.connector
from sshtunnel import SSHTunnelForwarder
import socket

tuxmlDB = None

if(socket.gethostname() != 'tuxmlweb'):
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



@app.route('/stats')
def stats():
    cursor = tuxmlDB.cursor()
    cursor.execute("SELECT COUNT(compiled_kernel_size) FROM compilations WHERE compiled_kernel_size < 0")
    nbcompilfailed = cursor.fetchone()[0]
    cursor.execute("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version ASC")
    versions = cursor.fetchall()

    return render_template('stats.html', nbcompilfailed=nbcompilfailed, versions=versions)

@app.route('/test1')
def hello():
    return 'Hello, World!'


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=8000)
