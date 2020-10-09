from flask import Flask
from flask import render_template
import os
import mysql.connector
from sshtunnel import SSHTunnelForwarder
import socket

tuxmlDB = None

if(socket.gethostname() != 'tuxmlweb'):
	print("Connexion à la BDD en passant par le serveur web (SSH)")
	tunn = SSHTunnelForwarder(
			('tuxmlweb.istic.univ-rennes1.fr', 22),
			ssh_username='zprojet',
			ssh_pkey='../keys/cle',
			remote_bind_address=('148.60.11.195', 3306))
	tunn.start()
	print("Connecté au serveur web (SSH), connexion à la BDD")
	tuxmlDB = mysql.connector.connect(
		host='148.60.11.195',
		port=3306,
		user='web',
		password='df54ZR459',
		database='IrmaDB_result')
else:
	print("Connexion directe à la BDD")
	tuxmlDB = mysql.connector.connect(
		host='148.60.11.195',
		port=3306,
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
	return render_template('stats.html')

@app.route('/test1')
def hello():
	return 'Hello, World!'


if __name__ == "__main__":
	from waitress import serve
serve(app, host="127.0.0.1", port=8000)
