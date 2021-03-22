#!/usr/bin/python3
import os
import sys
import shutil
from dbRequest import *


PATH = "../../downloads/"

#If foldername don t exist create the directory and change the working directory to foldername
def checkDirectory(foldername):
    path = PATH + foldername

    if os.path.exists(path):
        pass
    else :
        try:        
            os.mkdir(path)
        except OSError:
            print ("Failure Creation of the directory : %s " % path)
            sys.exit()
    
    try:
        os.chdir(path)
    except OSError:
        print ("Failure Change current working directory to : %s " % path)
        sys.exit()

        
    pathConfig = "./configs"
    if os.path.exists(pathConfig):
        pass
    else :
        try:        
            os.mkdir(pathConfig)
        except OSError:
            print ("Failure Creation of the directory : %s " % pathConfig)
            sys.exit()
    
    try:
        os.chdir(pathConfig)
    except OSError:
        print ("Failure Change current working directory to : %s " % pathConfig)
        sys.exit()



#Check if the selected version exists
def checkVersion(version):
    _versionQuery = read_query("SELECT DISTINCT compiled_kernel_version FROM compilations;")
    _allVersion = [ver[0] for ver in _versionQuery]
    
    if version not in _allVersion:
	    print("Failure Wrong version choose : %s" % version)
	    sys.exit()


#get the last cid used        
def getLastCid():
    if os.path.exists("../cid_list"):
        f = open("../cid_list", "r")
        for last_line in f:
            pass
        f.close()
        return last_line.rstrip('\n')
    else:
        return 0
    

#Create a directory and download in this directory files from a selected version.
def getConfig(version):
    
    #Check the version
    if version != "all":
        checkVersion(version)
        _versionSelect = f" WHERE compiled_kernel_version='{version}'"
    else :
        _versionSelect = ""
        
    #Check the directory
    checkDirectory(version)

    
    print("")
    
    #Get cid
    _lastCid = getLastCid()
    if version == "all":
        _finalQuery = f"SELECT cid FROM compilations WHERE cid > {_lastCid} ORDER BY cid LIMIT 1;"
    else :
        _finalQuery = f"SELECT cid FROM compilations {_versionSelect} AND cid > {_lastCid}  ORDER BY cid LIMIT 1;"
    _CompilIDs = read_query(_finalQuery)


    
    for _compilID in _CompilIDs:

        #on extrait et on cast l'ID de chaque élement de _CompilIDs
        cplID = str(_compilID[0])


        

        #si le dossier de la compilation n'existe pas on le créé
        if not os.path.isdir(cplID):
            os.makedirs(cplID)

        #si le dossier est vide on télécharge les fichiers
        if not os.listdir(cplID):
            #on rentre dans ce dossier
            os.chdir(fr"./{cplID}")

            #liste des fichiers de la base de données
            _filenameList = ["config_file"]

            #recupération des fichiers
            for filename in _filenameList:
                #on vérifie que le fichier n'existe pas déjà
                if not os.path.exists(filename):
                    #on récupère le fichier dans la base de données
                    print(f"Downloading {filename} compilation {cplID}")
                    file = get_file(cplID,filename)
                    #si le fichier est vide on ne l'enregistre pas
                    if file != "" and file is not None:
                        f = open(f"{filename}","w+")
                        f.write(file)
                        f.close()

            #on retourne dans le dossier parent
            os.chdir("..")
            
        f = open("../cid_list", "a")
        line = cplID + "\n"
        f.write(line)
        f.close()
        
        cwd = os.getcwd()  # Get the current working directory (cwd)
        
        
    os.chdir("..")    
    os.chdir("..")



