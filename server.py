#!/usr/bin/python3
import bz2
from  distutils import util
import signal
from io import BytesIO
from time import sleep
import threading
from flask_caching import Cache
from flask import Flask, render_template, url_for, request, send_file, redirect, abort, session, jsonify
import os
import mysql.connector
import socket
import sys
from os import path
import waitress
import dbManager


app = Flask(__name__, template_folder=os.path.abspath('templates'))
app.config['SECRET_KEY'] = '71794b6f6130464a494b6e62634b7167594b5850'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.context_processor
def time_formatter():
    def format_time(amount):
        m, s = divmod(amount, 60)
        return '{:02d} min {:02d} sec'.format(int(m), int(s))
    return dict(format_time=format_time)
    
@app.context_processor
def size_formatter():
    def format_size(amount, unit):
        return '{:.2f} {:s}'.format(round(amount/1000000, 2), unit)
    return dict(format_size=format_size)

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
    return render_template('base.html', count=dbManager.getCompilationCount())

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

    if sortBy is None : # or not(sortBy == "sic" or sortBy == "compilation_date" or sortBy == "compilation_time" or sortBy == "compiled_kernel_size" or sortBy == "compiled_kernel_version"): #On ne peut pas obtenir les colonnes (Droits refusés pour Web), du coup go hardcoder :/
        sortBy = "cid"

    if laversion is None :
        laversion = "All"
    else:
        laversion.replace(";", "").replace("\\","")

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
    url_interest = ""
    for e in interest:
        str_interest = str_interest + ", compilations." + e + " "
        url_interest = url_interest + "&interest=" + e


    interest_software = request.args.getlist('interest_software')
    str_interest_software = ""
    url_interest_software = ""
    str_interest_software_left_join = ""
    for e in interest_software :
        str_interest_software = str_interest_software + ", software_environment." + e + " "
        url_interest_software = url_interest_software + "&interest_software=" + e

    if interest_software is not None :
        str_interest_software_left_join = " LEFT JOIN software_environment ON compilations.sid = software_environment.sid "





    versions = [["All"]] + dbManager.getExistingKernelVersions()
    temp = dbManager.makeRequest("SELECT b.* FROM (SELECT a.* FROM (SELECT compilations.cid " + str_interest + str_interest_software + " FROM compilations " + str_interest_software_left_join + ("" if laversion == "All" else f"WHERE compiled_kernel_version = '{laversion}'")+ f" ORDER BY {sortBy} {'ASC' if ascend else 'DESC'} LIMIT " + str(numberOfNupletTemp) + f")a ORDER BY {sortBy} {'DESC' if ascend else 'ASC'} LIMIT  " +  str(numberOfNuplet) + f")b ORDER BY {sortBy} {'ASC' if ascend else 'DESC'} ;")
    count = dbManager.getCompilationCount(laversion)





    #modify the values contained in the query to adapt the reading to a human
    ten=[]
    line = []
    i = -1

    if(isinstance(temp[0], int)):
        temp = [temp]
    for row in temp :
        for e in row :
            if i == -1:
                line = [str(e)]
            elif i < len(interest):
                if interest[i] == "compiled_kernel_size" :
                    if e == -1:
                        line.append("Compilation failed")
                    else :
                        line.append('{:.2f} Mo'.format(round(e/1000000, 2)))
                elif interest[i] == "compilation_time" :
                    m, s = divmod(e, 60)
                    line.append('{:02d} min {:02d} sec'.format(int(m), int(s)))
                else:
                    line.append(str(e))
            else :
                line.append(str(e))
            i = i + 1
        i = -1
        ten.append(line)


    #query_compare_compilation
    compare = request.args.get('compare')
    temp_compare_cid_list = request.args.getlist('compare_cid_list')
    remove_compare_cid = request.args.get('remove_compare_cid')

    if compare is None :
        compare = False

        #remove remove_compare_cid from compare_cid_list
    compare_cid_list = []
    for cid in temp_compare_cid_list :
        if cid != remove_compare_cid :
            compare_cid_list.append(cid)


    str_compare_cid_list = ""
    url_compare_cid_list = ""
    firstloop = True
    for e in compare_cid_list :
        if firstloop :
            str_compare_cid_list = " '" + e + "' "
            firstloop = False
        else :
            str_compare_cid_list = str_compare_cid_list + " ,'" + e + "' "
        url_compare_cid_list = url_compare_cid_list + "&compare_cid_list=" + e

    query_compare_compilation=[]
    if len(compare_cid_list) > 0:
        temp_query_compare_compilation = dbManager.makeRequest("SELECT compilations.cid " + str_interest + str_interest_software + " FROM compilations " + str_interest_software_left_join + " WHERE cid IN (" + str_compare_cid_list + ") ;")
        #modify the values contained in the query to adapt the reading to a human
        line = []
        i = -1
        if len(compare_cid_list) > 1 :
            for row in temp_query_compare_compilation :
                for e in row :
                    if i == -1:
                        line = [str(e)]
                    elif i < len(interest):
                        if interest[i] == "compiled_kernel_size" :
                            if e == -1:
                                line.append("Compilation failed")
                            else :
                                line.append('{:.2f} Mo'.format(round(e/1000000, 2)))
                        elif interest[i] == "compilation_time" :
                            m, s = divmod(e, 60)
                            line.append('{:02d} min {:02d} sec'.format(int(m), int(s)))
                        else:
                            line.append(str(e))
                    else :
                        line.append(str(e))
                    i = i + 1
                i = -1
                query_compare_compilation.append(line)
        elif len(compare_cid_list) == 1 :
            for e in temp_query_compare_compilation :
                    if i == -1:
                        line = [str(e)]
                    elif i < len(interest):
                        if interest[i] == "compiled_kernel_size" :
                            if e == -1:
                                line.append("Compilation failed")
                            else :
                                line.append('{:.2f} Mo'.format(round(e/1000000, 2)))
                        elif interest[i] == "compilation_time" :
                            m, s = divmod(e, 60)
                            line.append('{:02d} min {:02d} sec'.format(int(m), int(s)))
                        else:
                            line.append(str(e))
                    else :
                        line.append(str(e))
                    i = i + 1
            query_compare_compilation.append(line)

    return render_template('data.html', laversion=laversion, numberOfNuplet=numberOfNuplet, page=page, versions=versions, ten=ten, sortBy=sortBy, ascend=ascend, count=count, interest=interest, url_interest=url_interest, interest_software=interest_software, url_interest_software=url_interest_software, query_compare_compilation=query_compare_compilation, compare=compare, compare_cid_list=compare_cid_list, url_compare_cid_list=url_compare_cid_list)



@app.route('/data/configuration/<int:id>/')
@cache.cached(timeout=10000000, query_string=True)
def user_view(id):
    confData = dbManager.getCompilationInfo(id)
    if confData is None:
        return abort(404)
    return render_template('config.html', config=confData.compilationInfo, sconfig=confData.softwareInfo, hconfig=confData.hardwareInfo)

@app.route('/data/configuration/<int:id>/<string:request>')
def getData(id, request):

    if not dbManager.compilationExists(id):
        return abort(404)

    requestedFile = dbManager.getCompilationFile(id,request)

    if requestedFile is None or not dbManager.compilationExists(id):
        return abort(500)

    return send_file(BytesIO(requestedFile), as_attachment=True, attachment_filename=f"TuxML-{id}.{request + ('.log' if (request!='config') else '') }")

@app.route('/api/v1/resources/compilations', methods=['GET'])
def api_filter():
    query_parameters = request.args

    cid = query_parameters.get('cid')
    
    if cid:
        query = dbManager.programmaticRequest(getColumn=None, withConditions=f"cid = {cid}", caching= False, execute=False)
    if (not cid or not dbManager.compilationExists(cid)):
        return abort(404)
    
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()[0]
    
    d = dict_factory(cursor, query_result)
    d = dict_formatting(d, cid)

    return jsonify(d)
    
def dict_factory(cursor, query_list):
    d = {}
    for i, v in enumerate(cursor.description):
        d[v[0]] = query_list[i]
    return d

def dict_formatting(d, cid):
    if 'config_file' in d:
        d['config_file'] = os.path.join(request.url_root, url_for('getData', id=cid, request='config')[1:])
    if 'stdout_log_file' in d:
        d['stdout_log_file'] = os.path.join(request.url_root, url_for('getData', id=cid, request='stdout')[1:])
    if 'stderr_log_file' in d:
        d['stderr_log_file'] = os.path.join(request.url_root, url_for('getData', id=cid, request='stderr')[1:])
    if 'user_output_file' in d:
        d['user_output_file'] = os.path.join(request.url_root, url_for('getData', id=cid, request='userOutput')[1:])
    if 'hid' in d:
        del d['hid']
    if 'sid' in d:
        del d['sid']
    return d

if __name__ == "__main__":
    arg = 8000
    if len(sys.argv) == 2:
        arg = str(sys.argv[1])
    if(socket.gethostname() != 'tuxmlweb'):
        app.debug = True

    waitress.serve(app, host="127.0.0.1", port=arg, threads=9)
    
