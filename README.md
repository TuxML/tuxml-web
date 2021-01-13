# tuxml-web

tuxmlweb.istic.univ-rennes1.fr

## How to continue development from your machine

You will need the following packages :
```
sudo apt install python3-flask
sudo pip3 install mysql-connector-python waitress flask-caching arrow
```

If you're using the ISTIC's VPN or are using the ISTIC's WIFI network, you can start the server directly :
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


# Queries library documentation
## "Smart caching" system
Behind this name is a simple way to keep data as fresh as possible without having to overwhelm the database with requests, as a complementary to flask-caching.

+ The system will periodically refresh the cache items according to their frequency of use (From to every 5 minutes to each 50 minutes).

+ Every 6 hours, the cache will be purged of items that haven't been used in 24 hours.

+ Cached items with the passiveData flag will never be refreshed or deleted from the cache, so **use the flag wisely.**

Note : The behavior of the passiveData-flagged cache items will be improved in the future

## Methods
### makeRequest
`makeRequest(query, caching = True, isPassiveData = False)`

If **caching** is set to False :

+ Makes a request to the database
+ Unfolds the result (up to two times) if necessary.

else :

+ Checks if the specified `query` already exists in the cache. And returns what's cached it if so.
+ If not, it makes a request, unfolds it, save it into the cache and returns it.


The `isPassiveData` option allows to create cache items with the passiveData flag, with the exact same impact than written above.

### getCompilationCount
`getCompilationCount(specificVersion = None)`

Returns the number of compilation made for a specified kernel version.

If `specificVersion` is unspecified, or set to 'All', then the total number of compilations will be returned.

### compilationExists
`compilationExists(compilationId)`

Returns if the specified compilation id exists or not.

### getCompilationInfo - To be rewritten (Returned object will change)
`getCompilationInfo(compilationId, basic = False)`

Returns a `compilationInfo` object containing:
+ `compilationInfo.compilationInfo` : List containing informations about the requested configuration (compilation time, ...)
+ `compilationInfo.softwareInfo` : List containing informations about the software environment of the requested configuration
+ `compilationInfo.hardwareInfo` : List containing informations about the hardware environment of the requested configuration

The `basic` option returns the same object, but with `.softwareInfo` and `.hardwareInfo` set to None.

### getCompilationFile - To be updated (Needs more robustness)
`getCompilationFile(compilationId, requestedFileType)`

Returns the file requested (specified with `requestedFileType`) for the compilation `compilationId`. Returns None if the file is broken or not found.

 `requestedFileType` can be `'config'`, `'stdout'`, `'stderr'` or `'userOutput'`
 
### getColumnsForCompilationsTable
`getColumnsForCompilationsTable(includeBlobs = False)`

Utilitary option that returns a list of the columns of the 'compilations' table.
Set the `includeBlobs` option to True to get the blobs-containing columns as well.

### getColumnsForHardwareEnvTable
`getColumnsForhardwareEnvTable()`

Utilitary option that returns a list of the columns of the 'hardware_environment' table.

### getColumnsForSoftwareEnvTable
`getColumnsForSoftwareEnvTable()`

Utilitary option that returns a list of the columns of the 'software_environment' table.

### getExistingKernelVersions - To be updated (Param name)
`getExistingKernelVersions(desc = False)`

Returns the list of the kernel versions that have been compiled in the database.
Set `desc` to true to invert the order of the list (From increasing ordre to decreasing).

### getNumberOfActiveOptions
`getNumberOfActiveOptions(compilationId)`

Returns the number of active options for a specific `compilationId`.
