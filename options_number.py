import bz2
import mysql.connector
import socket
import sys
import statistics
# Use: statistics.mean(liste) 
from statistics import mean
# Use: mean(liste)
from os import path
def get_configuration_file(cid):
    #print("Getting configuration file of cid=", cid)
    try:
        socket = mysql.connector.connect(
            host='148.60.11.195',
            user='web',
            password='df54ZR459',
            database='IrmaDB_result')
        cursor = socket.cursor()
        query = "SELECT config_file FROM compilations WHERE cid = %d" % cid
        cursor.execute(query)
        config_file = cursor.fetchone()
        if (config_file is None):
            print("Unable to retrieve cid=", str(cid))
            return
        try:
            return bz2.decompress(config_file[0]).decode('ascii')
        except Exception as e:
            print(str(e), "\n" + "Unable to decompress... ", file=sys.stderr)
            exit(-1)
    except Exception as e:
        print(str(e), "\n" + "Unable to connect to database cid = " + str(cid), file=sys.stderr)
        exit(-1)
    finally:
        cursor.close()
        socket.close()
#cf1 = get_configuration_file(116733)

#return 10 last cid of correctly compiled version v  
def get_list_of_cid_for_version(v):
    v_liste = [4.13, 4.15, 4.16, 4.17, 4.18, 4.20, 5.0, 5.1, 5.10, 5.4, 5.7, 5.8, 5.9]
    x=[]
    if (v not in v_liste):
            print("This version does not exist ! ")
            return
    try:
        #connecting to the database
        socket = mysql.connector.connect(
            host='148.60.11.195',
            user='web',
            password='df54ZR459',
            database='IrmaDB_result')
        #create a cursor    
        cursor = socket.cursor()
        #sql query
        query = "SELECT cid FROM compilations WHERE compiled_kernel_version = %f and compiled_kernel_size > 0 order by cid desc limit 10" %v
        cursor.execute(query)
        l = cursor.fetchall()
        for row in l:
            x.append(row[0])
 
        #if cid not found 
   
    except Exception as e:
        print(str(e), "\n" + "Unable to connect to database cid = " + str(cid), file=sys.stderr)
        exit(-1)
    #close the socket and the cursor    
    finally:
        return x
        cursor.close()
        socket.close()
#y=get_list_of_cid_for_version(5.0)     
#print(y)

#return number of options in a specified file
def options_number(cpt):
            j=0 
            for i, line in enumerate(cpt):
                # on ne concidere que les options valides à 'y' ou 'm' ou des valeurs entière/string
                if line.startswith('C'):
                    j +=1
            return j 
#return a list of number of options
def options(x):
            l =[]
            for i in x:
                l.append(options_number(get_configuration_file(i)))
            return l  
#return la moyennes des options pour une version donnée            
def moyenne(y):
            m = mean(y)
            return m  
#return la liste des moyennes de toutes les versions            
def liste_de_moyenne():
    v_liste = [4.13, 4.15, 4.16, 4.17, 4.18, 4.20, 5.0, 5.1, 5.10, 5.4, 5.7, 5.8, 5.9] 
    length = len(v_liste)    
    l = []
    i=0
    while i < length:
        x = get_list_of_cid_for_version(v_liste[i])
        y = options(x)
        l.append(moyenne(y))
        i += 1
    return l    
