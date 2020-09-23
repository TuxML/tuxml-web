from flask import Flask
from flask import render_template
import os
import mysql.connector
app = Flask(__name__, template_folder=os.path.abspath('templates'))
    
@app.route('/')
def hello_world():
	tuxmlDB = mysql.connector.connect(
        host='148.60.11.195',
        user='web',
        password='df54ZR459',
        database='IrmaDB_result')

	mycursor = tuxmlDB.cursor()
	mycursor.execute("SELECT COUNT(*) FROM compilations")
	nbcompil = mycursor.fetchone()[0]

	return render_template('base.html',count=nbcompil)

@app.route('/test1')
def hello():
    return 'Hello, World!'

if __name__ == "__main__":
	from waitress import serve
	serve(app, host="148.60.11.219", port=80)
