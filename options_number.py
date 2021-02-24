import bz2
import mysql.connector
import socket
import sys
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

#return 10 last cid of correctly compiled version 5.0  
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
        query = "SELECT cid FROM compilations WHERE compiled_kernel_version = 5.0 and compiled_kernel_size > 0 order by cid desc limit 10"
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

def options_number(cpt):
            j=0 
            for i, line in enumerate(cpt):
                
                if '#' not in line:
                    j +=1
            return j 

def options(x):
            l =[]
            for i in x:
                l.append(options_number(get_configuration_file(i)))
            return l       
#print(options(get_list_of_cid_for_version(5.0))