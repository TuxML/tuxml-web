import bz2
import mysql.connector
import socket
import sys
from os import path
def get_configuration_file(cid):
    print("Getting configuration file of cid=", cid)
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
cf1 = get_configuration_file(116733)
#print(cf1)
with open(cf1) as f:
            j=0 
            for i, line in enumerate(f):
                
                if line.startswith('# CONFIG'):
                    j +=1
        return j 
print("Number of configuration in this file is: ",file_lengthy("test1.bin.out"))