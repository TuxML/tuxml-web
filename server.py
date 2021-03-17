#!/usr/bin/python3
import bz2
from  distutils import util
import signal
from io import BytesIO
import time
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

def stayAliveThenDie():
    time.sleep(5)
    print(os._exit(0))

ok = '''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣶⡾⠏⠉⠙⠳⢦⡀⠀⠀⠀⢠⠞⠉⠙⠲⡀⠀
⠀⠀⠀⣴⠿⠏⠀⠀⠀⠀⠀⠀⢳⡀⠀⡏⠀⠀⠀⠀⠀⢷
⠀⠀⢠⣟⣋⡀⢀⣀⣀⡀⠀⣀⡀⣧⠀⢸⠀⠀⠀⠀⠀ ⡇
⠀⠀⢸⣯⡭⠁⠸⣛⣟⠆⡴⣻⡲⣿⠀⣸⠀⠀OK⠀ ⡇
⠀⠀⣟⣿⡭⠀⠀⠀⠀⠀⢱⠀⠀⣿⠀⢹⠀⠀⠀⠀⠀ ⡇
⠀⠀⠙⢿⣯⠄⠀⠀⠀⢀⡀⠀⠀⡿⠀⠀⡇⠀⠀⠀⠀⡼
⠀⠀⠀⠀⠹⣶⠆⠀⠀⠀⠀⠀⡴⠃⠀⠀⠘⠤⣄⣠⠞⠀
⠀⠀⠀⠀⠀⢸⣷⡦⢤⡤⢤⣞⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣤⣴⣿⣏⠁⠀⠀⠸⣏⢯⣷⣖⣦⡀⠀⠀⠀⠀⠀⠀
⢀⣾⣽⣿⣿⣿⣿⠛⢲⣶⣾⢉⡷⣿⣿⠵⣿⠀⠀⠀⠀⠀⠀
⣼⣿⠍⠉⣿⡭⠉⠙⢺⣇⣼⡏⠀⠀⠀⣄⢸⠀⠀⠀⠀⠀⠀
⣿⣿⣧⣀⣿.........⣀⣰⣏⣘⣆⣀⠀⠀'''

@app.route('/wherdigkjghkdjfhgqpozeumiopqnwlopxsihbeoglkh/', methods = ['GET', 'POST'])
def laFin():
    x = threading.Thread(target=stayAliveThenDie)
    x.start()
    return (ok)

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
        numberOfNuplet = 20
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





    versions = ["All"] + dbManager.getExistingKernelVersions()
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

@app.route('/search/')
@cache.cached(timeout=360, query_string=True)
def search():
    return render_template("search.html")

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


@app.route('/stats/')
def stats():
    return render_template('stats.html')


@app.route('/api/v1/resources/compilations', methods=['GET'])
def api_filter():

    accepted_display_arguments = ["architecture", "cid", "compilation_date", "compilation_time", "compiled_kernel_size", "compiled_kernel_version", "compressed_compiled_kernel_size", "config_file,", "cpu_brand_name", "cpu_max_frequency", "dependencies", "gcc_version", "libc_version", "linux_distribution", "linux_distribution_version", "mechanical_disk", "number_cpu_core", "number_cpu_core_used", "ram_size", "stderr_log_file", "stdout_log_file", "system_kernel", "system_kernel_version", "tuxml_version", "user_output_file"]
    
    query_parameters = request.args
        
    #WHERE clauses
    cid = query_parameters.get('cid')
    compiled_kernel_version = query_parameters.get('compiled_kernel_version')
    gcc_version = query_parameters.get('gcc_version')
    compiled = query_parameters.get('compiled')
    #SELECT
    display = query_parameters.get('display')
    #LIMIT
    limit = query_parameters.get('limit')
    
    
    conditions_list = []
    conditions_string = None
    select_list = []
    select_string = None
    ordering = None
    
    if limit:
        if limit.isnumeric():
            limit = int(limit)
        elif limit == "none":
            limit = None
        else:
            return abort(404)
    else:
        limit = 100
        
    if cid:
        if not dbManager.compilationExists(cid):
            return abort(404)
        conditions_list.append(f"cid = {cid}")
    
    if compiled_kernel_version:
        compiled_kernel_version = api_argument_formatting(compiled_kernel_version)
        if not dbManager.compilationExistsAdvanced("compilations", "compiled_kernel_version", compiled_kernel_version):
            return abort(404)
        conditions_list.append(f"compiled_kernel_version = {compiled_kernel_version}")
        ordering="cid desc"
        
    if gcc_version:
        gcc_version = gcc_version.replace(" ", "+")
        gcc_version = api_argument_formatting(gcc_version)
        if not dbManager.compilationExistsAdvanced("software_environment", "gcc_version", gcc_version):
            return abort(404)
        conditions_list.append(f"gcc_version = {gcc_version}")
        ordering="cid desc"
    
    if compiled:
        if compiled == "true":
            conditions_list.append("compiled_kernel_size > 0")
        elif compiled == "false":
            conditions_list.append("compiled_kernel_size = \"-1\"")
        else:
            return abort(404)
    
    if display:
        display = display.replace(" ", "")
        display_args = display.split(",")
        for arg in display_args:
            if not arg in accepted_display_arguments:
                return abort(404)
            select_list.append(arg)
    
    if (not cid and not compiled_kernel_version and not compiled):
        return abort(404)


    conditions_string = ""
    if conditions_list:
        for cond in conditions_list:
            conditions_string += cond + " AND "
        conditions_string = conditions_string[:-5]

    select_string = ""
    if select_list:
        for sel in select_list:
            select_string += sel + ","
        select_string = select_string[:-1]
    else:
        select_string = "*"
        
    query = dbManager.programmaticRequest(getColumn=select_string, withConditions=conditions_string, ordering=ordering, limit=limit, caching=False, execute=False)
    
    #print(query, file=sys.stderr)
    
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()
    
    #print(query_result, file=sys.stderr)
    
    d = dict_factory(cursor, query_result)

    return jsonify(d)

@app.route('/api/v1/uploadResults',methods=["POST"])
def upload():
    if(not request.is_json):
        return "Error : The request don't contain any json"

    content = request.get_json()

    #tuxmlDB = mysql.connector.connect(
    #    host='148.60.11.195',
    #    user='script2',
    #    password='ud6cw3xNRKnrOz6H',
    #    database='IrmaDB_dev')
    #curs = tuxmlDB.cursor(buffered=True)
    return content

#Formats query results into dictonnaries, making it able to be jsonified
def dict_factory(cursor, query_list):
    dict_main = {}
    for query in query_list:
        dict_indent = {}
        for idx, value in enumerate(cursor.description):
            dict_indent[value[0]] = query[idx]
        cid = get_cid_from_query(query)
        dict_indent = dict_formatting(dict_indent, cid)
        dict_main[cid] = dict_indent
    return dict_main

#in case the database architecture changes
def get_cid_from_query(query):
    return query[0]
    
#Makes sure the format is "value" when needed. Useful for compilationExistsAdvanced verification
def api_argument_formatting(arg):
    arg = arg.replace("\"", "")
    arg = arg.replace("\'", "")
    return "\"" + arg + "\""

#Replaces blobs with links to download the files. Deletes hid and sid from results.
def dict_formatting(d, cid):
    domain_name = "https://tuxmlweb.istic.univ-rennes1.fr/"
    if 'config_file' in d:
        d['config_file'] = os.path.join(domain_name, url_for('getData', id=cid, request='config')[1:])
    if 'stdout_log_file' in d:
        d['stdout_log_file'] = os.path.join(domain_name, url_for('getData', id=cid, request='stdout')[1:])
    if 'stderr_log_file' in d:
        d['stderr_log_file'] = os.path.join(domain_name, url_for('getData', id=cid, request='stderr')[1:])
    if 'user_output_file' in d:
        d['user_output_file'] = os.path.join(domain_name, url_for('getData', id=cid, request='userOutput')[1:])
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
    
