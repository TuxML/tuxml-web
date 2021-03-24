#!/usr/bin/python3
import mysql.connector
import bz2

def create_server_connection():
	connection = None
	try:
		connection = mysql.connector.connect(
		host='148.60.11.195',
		user='web',
		password='df54ZR459',
		database='IrmaDB_result')
#		print("MySQL Database connection successful")

	except:
		print("Erreur de connection à la base de données")

	return connection



def read_query(query):
	connection = create_server_connection()
	cursor = connection.cursor()
	result = None
	try:
#		print("MySQL Database query execution")
		cursor.execute(query)

		result = cursor.fetchall()

		cursor.close()
#		print("MySQL Database cursor closed")

		connection.close()
#		print("MySQL Database connection closed\n")

		return result
	except:
		print("Erreur lors de l'envoi de la requete")

def get_file(cid,filename):

	if filename == "boot_log_file":
		result = read_query(f"SELECT {filename} FROM boot WHERE cid = {cid};")
	else:
		result = read_query(f"SELECT {filename} FROM compilations WHERE cid = {cid};")

	try:	
		return bz2.decompress(result[0][0]).decode('ascii')
	except:
		print(f"Erreur lors de la décompression du fichier {filename} de la compilation {cid}\n")