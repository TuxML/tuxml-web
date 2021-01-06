#!/usr/bin/python3
import bz2
import signal
from io import BytesIO
from time import sleep
import threading
from flask import Flask, render_template, url_for, request, send_file
import os
import mysql.connector
import socket
import sys
from os import path
import waitress

app = Flask(__name__, template_folder=os.path.abspath('templates'))



def getConnection():
    if (path.exists("tunnel")):
        tuxmlDB = mysql.connector.connect(
            host='localhost',
            port=20000,
            user='web',
            password='df54ZR459',
            database='IrmaDB_result')
    else:
        tuxmlDB = mysql.connector.connect(
            host='148.60.11.195',
            user='web',
            password='df54ZR459',
            database='IrmaDB_result')
    return tuxmlDB

@app.route('/')
def hello_world():
    connection = getConnection()
    mycursor = connection.cursor()
    mycursor.execute("SELECT COUNT(*) FROM compilations")
    nbcompil = mycursor.fetchone()[0]
    connection.close()
    return render_template('base.html', count=nbcompil)

@app.route('/wherdigkjghkdjfhgqpozeumiopqnwlopxsihbeoglkh/', methods = ['GET', 'POST'])
def laFin():
    print(os._exit(0)) #On ferme le serveur, systemd s'occupe de faire un git pull et de le relancer
    return ("¯\_(ツ)_/¯")

@app.route('/data/')
def data():
    connection = getConnection()
    cursor = connection.cursor()

    laversion = request.args.get('laversion')
    numberOfNuplet = request.args.get('numberOfNuplet')
    page = request.args.get('page')

    if laversion is None :
        laversion = "4.13.3"
    else:
        laversion.replace(";", "").replace("\\","")

    if numberOfNuplet is None :
        numberOfNuplet = 10
    else:
        numberOfNuplet.replace(";", "").replace("\\","")

    if page is None :
    	page = 1

    numberOfNupletTemp = int(numberOfNuplet) * int(page)
    page = int(page)



    cursor.execute("SELECT COUNT(compiled_kernel_size) FROM compilations WHERE compiled_kernel_size < 0 AND compiled_kernel_version = '{}';".format(laversion))
    versionreq = cursor.fetchall()
    cursor.execute("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version ASC")
    versions = cursor.fetchall()
    cursor.execute("SELECT b.* FROM (SELECT a.* FROM (SELECT cid, compilation_date, compilation_time, compiled_kernel_size, compiled_kernel_version FROM compilations WHERE compiled_kernel_version = '" + laversion + "' ORDER BY cid DESC LIMIT " + str(numberOfNupletTemp) + ")a ORDER BY cid ASC LIMIT  " +  str(numberOfNuplet) + ")b ORDER BY cid DESC ;")

    ten = cursor.fetchall()
    connection.close()
    return render_template('data.html', laversion=laversion, numberOfNuplet=numberOfNuplet, page=page, versionreq=versionreq, versions=versions, ten=ten)

@app.route('/data/configuration/<int:id>/')
def user_view(id):
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM compilations WHERE cid = " + str(id))
    config = cursor.fetchone()
    if config is None :
        return data()
    cursor.execute("SELECT * FROM software_environment WHERE sid = " + str(config[12]))
    sconfig = cursor.fetchone()
    cursor.execute("SELECT * FROM hardware_environment WHERE hid = " + str(config[13]))
    hconfig = cursor.fetchone()
    connection.close()
    return render_template('config.html', config=config, sconfig=sconfig, hconfig=hconfig)

@app.route('/data/configuration/<int:id>/<string:request>')
def getData(id, request):
    connection = getConnection()
    cursor = connection.cursor()
    returnAction = None
    if request == "config" :
        cursor.execute("SELECT * FROM compilations WHERE cid = " + str(id))
        returnAction = send_file(BytesIO(bz2.decompress(cursor.fetchone()[3])), as_attachment=True, attachment_filename="TuxML-"+str(id)+".config")
    elif request == "stdout" :
        cursor.execute("SELECT * FROM compilations WHERE cid = " + str(id))
        returnAction = send_file(BytesIO(bz2.decompress(cursor.fetchone()[4])), as_attachment=True, attachment_filename="TuxML-"+str(id)+"-stdout.log")
    elif request == "stderr" :
        cursor.execute("SELECT * FROM compilations WHERE cid = " + str(id))
        returnAction = send_file(BytesIO(bz2.decompress(cursor.fetchone()[5])), as_attachment=True, attachment_filename="TuxML-"+str(id)+"-stderr.log")
    elif request == "userOutput" :
        cursor.execute("SELECT * FROM compilations WHERE cid = " + str(id))
        returnAction = send_file(BytesIO(bz2.decompress(cursor.fetchone()[6])), as_attachment=True, attachment_filename="TuxML-"+str(id)+"-userOutput.log")
    connection.close()
    return returnAction

@app.route('/stats/2/')
def statslaversion():
    connection = getConnection()
    cursor = connection.cursor()
    laversion = request.args.get('laversion')
    cursor.execute("SELECT COUNT(compiled_kernel_size) FROM compilations WHERE compiled_kernel_size < 0 AND compiled_kernel_version = '{}';".format(laversion))
    versionreq = cursor.fetchall()
    cursor.execute("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version ASC")
    versions = cursor.fetchall()
    connection.close()
    return render_template('statsversion.html', laversion=laversion, versionreq=versionreq, versions=versions)

@app.route('/test1')
def hello():
    path = request.path
    method = request.method
    domain = request.base_url

    return 'path : ' + path + ' method : ' + method + 'domain' + domain


if __name__ == "__main__":
    arg = 8000
    if len(sys.argv) == 2:
            arg = str(sys.argv[1])
    if(socket.gethostname() != 'tuxmlweb'):
        app.debug = True
    waitress.serve(app, host="127.0.0.1", port=arg, threads=9)
    
