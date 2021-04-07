#!/usr/bin/python3
import os
import sys
from views import *
#from dbRequest import *


_bootFail = "WHERE"
_compilFail = "WHERE"


#Choix du chemin pour l'enregistrement des fichiers
while True:
	_path = input("Dans quel dossier enregistrer les fichiers de compil ? (chemin absolu) :\n")
	if not os.path.exists(_path):
		print("Veuillez entrer un chemin correct\n")
		continue
	break

os.chdir(_path)
print(f"\nchemin choisi : {os.getcwd()}\n")


#Choix de la version à télécharger
_versionQuery = read_query("SELECT DISTINCT compiled_kernel_version FROM compilations;") #tableau de la forme [(v1,),(v2,),(v3,)]
_allVersion = [ver[0] for ver in _versionQuery] #tableau avec le premier element de chaque tuples = liste des versions
while True:
	_versionSelect = input(f"De quelle version du kernel voulez vous les fichiers de compilations ? (0 = toutes) :\n{_allVersion}\n")
	if _versionSelect not in _allVersion:
		if _versionSelect == "0":
			_versionSelect = "compiled_kernel_version"
			break
		print("Veuillez choisir une version existante\n")
		continue
	break

print(f"version choisie : {_versionSelect}\n")
_versionSelect = f" WHERE compiled_kernel_version={_versionSelect}"


#Choix du nombre de fichiers à télécharger
while True:
	try:
		_nbCompilPerQuery = int(input("Combien de compilations voulez vous télécharger ? (0 = toutes) :\n"))
	except ValueError:
		print("Veuillez entrer un nombre\n")
		continue
	break



_finalQuery = f"SELECT cid FROM compilations{_versionSelect} ORDER BY compilation_date DESC LIMIT 0, {_nbCompilPerQuery};"
if(_nbCompilPerQuery == 0):
	_finalQuery = f"SELECT cid FROM compilations {_versionSelect} ORDER BY compilation_date DESC;"

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
		os.chdir(fr"{_path}\{cplID}")

		#liste des fichiers de la base de données
		_filenameList = ["config_file"]

		#recupération des fichiers
		for filename in _filenameList:
			#on vérifie que le fichier n'existe pas déjà
			if not os.path.exists(filename):
				#on récupère le fichier dans la base de données
				print(f"téléchargement du fichier {filename} de la compilation {cplID}")
				file = get_file(cplID,filename)
				#si le fichier est vide on ne l'enregistre pas
				if file != "" and file is not None:
					f = open(f"{filename}","w+")
					f.write(file)
					f.close()
				else:
					print("fichier vide, création annulée\n")

		#on retourne dans le dossier parent
		os.chdir(_path)

print("toutes les compilations ont été importées")