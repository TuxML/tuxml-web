# tuxml-web

## How to continue development from your machine

You will need the following packages :
```
sudo apt install python3-flask
sudo pip3 install mysql-connector-python waitress
```

If you're using the ISTIC's VPN or are using the ISTIC' WIFI network, you can start the server directly :
```
python3 server.py
```

Otherwise, you have to start the server this way :
```
bash startMe.sh
```
The script will start an SSH tunnel to the web server so you can get a tunnel access to the database.

### Important notes :

- You need to put the server's SSH key in an folder named 'keys' at the same level than this repo's level:
```
.
├── keys
│   └── cle <-- the SSH key (Name it 'cle', otherwise the SSH tunnel will not work)
└── tuxml-web <-- this repo
    ├── README.md
    ├── server.py
    ├── startMe.sh
    ├── static/
    └── templates/
```

- To exit the server and close properly the SSH tunnel, **just ^C it**. The server will exit and then the bash script will manage the tunnel's disconnection.

## How to manually connect to the web server

The key file permissions must be "-r--------", aka 0400

```
ssh zprojet@148.60.11.219 -i /pathofthekey
```
