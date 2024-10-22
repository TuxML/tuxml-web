import bz2
import mysql.connector
import socket
import sys
import dbRequest
import os
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
# cette fonction prend en parametre un chemin d'une option donnée et retourne une liste dans chaque élement est le fichier config
# et la version comme deuxieme parametre
# exemple pv : folder_path_4_18 pour designer le chemin du dossier contenant les compilations de la version 4.18
# exemple v : 4.18 pour designer la version 4.18
# la liste contient tous les fichiers configs d'une version donnée
def list_of_config_files(pv,v):
    x1 = get_list_of_cid_for_version(v)
    # la liste qui va contenir les fichiers configs
    l = []
    # on parcour le repertoir qui correspond à la version 
    for path, dirs, files in os.walk(pv):
        for i in dirs:
                w = pv + "/" + i + "/config_file" 
                
                with open(w, "r") as fichier:
                    y = fichier.read()
                    l.append(y)
    return l 

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

#return 10 last cid of correctly compiled version v  
def get_all_list_of_cid_for_version(v):
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
        query = "SELECT cid FROM compilations WHERE compiled_kernel_version = %f and compiled_kernel_size > 0 order by cid asc" %v
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


#retourne la list du nombre d'options pour tous les fichiers configs d'une version donnée
# le parametre pv correspond à un chemin d'une version donnée : exemple folder_path_4_18 pour designer la version 4.18 
def options2(pv,v):
            l = []
            s = list_of_config_files (pv,v)
            for i in s:
                l.append(options_number(i))   
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

#return la liste des moyennes de toutes les versions        
#pour prendre en concideration que les versions 4.* entrez 4 comme argument, pareil pour 5, et entrez n'importe quel autre chiffre pour 
#prendre en conciderartion toutes les versions    
def liste_de_toutes_les_moyennes(x):
    #v_liste = [4.13, 4.15, 4.16, 4.17, 4.18, 4.20, 5.0, 5.1, 5.10, 5.4, 5.7, 5.8, 5.9] 
    v_liste_4 = [4.2,4.15,4.16,4.17,4.18]
    v_liste_5 = [5.0,5.1,5.4,5.7,5.8,5.9,5.10]
    v_liste = [4.15,4.16,4.17,4.18,4.20,5.0,5.1,5.4,5.8,5.10,5.9,5.7]
    length_4 = len(v_liste_4)    
    length_5 = len(v_liste_5)    
    length = len(v_liste)    
    l = []
    if x == 4 :
        i=0
        while i < length_4:
            x = get_all_list_of_cid_for_version(v_liste_4[i])
            y = options2("C:/Users/zbouk/OneDrive/Bureau/Study/Second semester/Tuxml/Files-config/"+ str(v_liste_4[i]) ,v_liste_4[i])
            l.append(moyenne(y))
            i += 1
    elif x == 5 :
        i=0
        while i < length_5:
            x = get_all_list_of_cid_for_version(v_liste_5[i])
            y = options2("C:/Users/zbouk/OneDrive/Bureau/Study/Second semester/Tuxml/Files-config/"+ str(v_liste_5[i]) ,v_liste_5[i])
            #print(y)
            l.append(moyenne(y))
            i += 1
    else :
        i=0
        while i < length:
            x = get_all_list_of_cid_for_version(v_liste[i])
            y = options2("C:/Users/zbouk/OneDrive/Bureau/Study/Second semester/Tuxml/Files-config/"+ str(v_liste[i]) ,v_liste[i])
            #print(y)
            l.append(moyenne(y))
            i += 1
    return l     
