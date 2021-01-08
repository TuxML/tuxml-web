#!/usr/bin/python3
import bz2
from  distutils import util
import signal
from io import BytesIO
from time import sleep
import threading
from flask_caching import Cache
from flask import Flask, render_template, url_for, request, send_file
import os
import mysql.connector
import socket
import sys
from os import path
import waitress

app = Flask(__name__, template_folder=os.path.abspath('templates'))
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


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
@cache.cached(timeout=3600)
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
@cache.cached(timeout=360, query_string=True)
def data():
    connection = getConnection()
    cursor = connection.cursor()

    laversion = request.args.get('laversion')
    numberOfNuplet = request.args.get('numberOfNuplet')
    page = request.args.get('page')

    sortBy = request.args.get('sortBy')
    ascend = request.args.get('ascend')


    if ascend is None :
        ascend = False
    else:
        ascend = util.strtobool(ascend)

    if sortBy is None or not(sortBy == "sic" or sortBy == "compilation_date" or sortBy == "compilation_time" or sortBy == "compiled_kernel_size" or sortBy == "compiled_kernel_version"): #On ne peut pas obtenir les colonnes (Droits refusés pour Web), du coup go hardcoder :/
        sortBy = "cid"

    if laversion is None :
        laversion = "All"
        versionreq = "All"
    else:
        laversion.replace(";", "").replace("\\","")
        cursor.execute(f"SELECT COUNT(compiled_kernel_size) FROM compilations WHERE compiled_kernel_size < 0 AND compiled_kernel_version = '{laversion}';")
        versionreq = cursor.fetchall()

    if numberOfNuplet is None :
        numberOfNuplet = 10
    else:
        numberOfNuplet.replace(";", "").replace("\\","")

    if page is None or int(page) < 1:
        page = 1

    numberOfNupletTemp = int(numberOfNuplet) * int(page)
    page = int(page)
    numberOfNuplet = int(numberOfNuplet)


    interest = request.args.getlist('interest')
    str_interest = ""

    for e in interest:
        str_interest = str_interest + ", " + e + " "

    cursor.execute("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version ASC")
    versions = [["All"]] + cursor.fetchall()
    cursor.execute("SELECT b.* FROM (SELECT a.* FROM (SELECT cid, compiled_kernel_version " + str(str_interest) + "FROM compilations " + ("" if laversion == "All" else f"WHERE compiled_kernel_version = '{laversion}'")+ f" ORDER BY {sortBy} {'ASC' if ascend else 'DESC'} LIMIT " + str(numberOfNupletTemp) + f")a ORDER BY {sortBy} {'DESC' if ascend else 'ASC'} LIMIT  " +  str(numberOfNuplet) + f")b ORDER BY {sortBy} {'ASC' if ascend else 'DESC'} ;")
    temp = cursor.fetchall()
    cursor.execute("SELECT COUNT(cid) FROM compilations " + ("" if laversion == "All" else f"WHERE compiled_kernel_version = '{laversion}'")+ f" ;")
    count = cursor.fetchone()
    connection.close()
    
    count = count[0]
    ten = temp
    return render_template('data.html', laversion=laversion, numberOfNuplet=numberOfNuplet, page=page, versionreq=versionreq, versions=versions, ten=ten, sortBy=sortBy, ascend=ascend, count=count, interest=interest)


    """
    ten = []

    for e in temp:
    if e[3] == -1:
        ten.append((e[0],e[1],str(e[2]) + " s","Compilation failed",e[4]))
    else:
        ten.append((e[0],e[1],str(e[2]) + " s",(str(e[3]/1000000) + " Mo"),e[4]))
        """

@app.route('/data/configuration/<int:id>/')
@cache.cached(timeout=10000000, query_string=True)
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



if __name__ == "__main__":
    arg = 8000
    if len(sys.argv) == 2:
        arg = str(sys.argv[1])
    if(socket.gethostname() != 'tuxmlweb'):
        app.debug = True

    waitress.serve(app, host="127.0.0.1", port=arg, threads=9)
    
