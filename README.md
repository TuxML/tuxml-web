# tuxml-web

## how to continue development from your machine

You will need the following packages :
```
sudo apt install python3-flask
sudo pip3 install mysql-connector-python
sudo pip3 install waitress
sudo pip3 install sshtunnel
```

You can now start the server !
```
python3 server.py
```

(if you are not on the Istic network you will not be able to connect to the database)

## how to connect to the virtual machine website host

The key file permissions must be "-r--------"

```
ssh zprojet@148.60.11.219 -i /pathofthekey
```

You can disconnect with :

```
logout
```
## how to connect to the virtual machine database host

```
ssh root@148.60.11.195
```

Now you can connect to the database :

```
mysql -u 'web' -p
show databases;
use IrmaDB_result;
show tables;
DESCRIBE compilations;
```



