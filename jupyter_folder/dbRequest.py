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

