#!/usr/bin/python3
import os
import sys
import shutil
from dbRequest import *


#Create a directory a change the current working directory to the new directory
#If the directory already exists it will be deleted
def checkDirectory(foldername):
    path = "./" + foldername

    if os.path.exists(path):
        shutil.rmtree(path)
        print("Success Deletion of the directory : %s"  % path)
    
    try:        
        os.mkdir(path)
    except OSError:
        print ("Failure Creation of the directory : %s " % path)
        sys.exit()
    else:
        print ("Success Creation of the directory : %s " % path)

    try:
        os.chdir(path)
    except OSError:
        print ("Failure Change current working directory to : %s " % path)
        sys.exit()
    else:
        print ("Success Change current working directory to : %s " % os.getcwd())


#Check if the selected version exists
def checkVersion(version):
    _versionQuery = read_query("SELECT DISTINCT compiled_kernel_version FROM compilations;")
    _allVersion = [ver[0] for ver in _versionQuery]
    
    if version not in _allVersion:
	    print("Failure Wrong version choose : %s" % version)
	    sys.exit()
    else:
        print ("Success Version selection : %s" % version)


#Create a directory and download in this directory files from a selected version.
def getLogs(directory, version, numberOfFiles):
    checkDirectory(directory)

    #Check the version
    if version != "all":
        checkVersion(version)
        _versionSelect = f" WHERE compiled_kernel_version={version}"
    else :
        _versionSelect = ""
        print ("Success Version selection : %s" % version)

    #Check the number of files to download
    try:
        _nbCompilPerQuery = int(numberOfFiles)
    except ValueError:
        print("Failure Wrong number of files to download : %s" % numberOfFiles)
        sys.exit()
    else :
        if _nbCompilPerQuery < 0 :
            print("Failure Number of files to download must be >= 0")
            sys.exit()
        print("Success Number of files to download : %s" % numberOfFiles)

    print("")
    
    #Get cid
    if _nbCompilPerQuery == 0 and version == "all":
        _finalQuery = "SELECT cid FROM compilations ORDER BY compilation_date DESC;"
    elif _nbCompilPerQuery != 0 and version == "all":
        _finalQuery = f"SELECT cid FROM compilations ORDER BY compilation_date DESC LIMIT 0, {_nbCompilPerQuery};"
    elif _nbCompilPerQuery == 0 and version != "all":
        _finalQuery = f"SELECT cid FROM compilations {_versionSelect} ORDER BY compilation_date DESC;"
    else :
        _finalQuery = f"SELECT cid FROM compilations {_versionSelect} ORDER BY compilation_date DESC LIMIT 0, {_nbCompilPerQuery};"
    _lastCompilIDs = read_query(_finalQuery)



    for _compilID in _lastCompilIDs:

        #on extrait et on cast l'ID de chaque élement de _lastCompilIDs
        cplID = str(_compilID[0])

        #si le dossier de la compilation n'existe pas on le créé
        if not os.path.isdir(cplID):
            os.makedirs(cplID)

        #si le dossier est vide on télécharge les fichiers
        if not os.listdir(cplID):
            #on rentre dans ce dossier
            os.chdir(fr"./{cplID}")

            #liste des fichiers de la base de données
            _filenameList = ["config_file","stdout_log_file","stderr_log_file","user_output_file","boot_log_file"]

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

    print("All compilations have been imported\n")