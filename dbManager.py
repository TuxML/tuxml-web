import bz2
import sys
import threading
from os import path
from time import sleep
import mysql.connector
import arrow

class __CacheItem: #Encapsulation has been highly used in this class's methods in order to keep data integrity
    def __init__(self, passiveData = False):
        self.__lock = threading.Lock()
        self.lastUpdate = arrow.now()
        self.useCount = 0 # <-- Deprecated
        self.isPassiveData = passiveData
        self.__data = None
    def update(self, data, impact = True):
        self.__lock.acquire()
        self.__data = data
        if impact :
            self.useCount += 1 # <-- Deprecated
            self.lastUpdate = arrow.now()
        self.__lock.release()
    def getData(self):
        if self.isPassiveData:
            data = self.__data
            return data
        self.__lock.acquire()
        data = self.__data
        self.useCount += 1 # <-- Deprecated
        self.__lock.release()
        return data

'''

Handles queries, and unfolds them (up to two times).

'''
def __fetchData(query):
    if (path.exists("tunnel")): # If we're connected throuh a SSH tunnel
        tuxmlDB = mysql.connector.connect(
        host='localhost',
        port=20000,
        user='web',
        password='df54ZR459',
        database='IrmaDB_result')
    else: # If we're connected through ISTIC VPN or via ISTIC Wifi network.
        tuxmlDB = mysql.connector.connect(
        host='148.60.11.195',
        user='web',
        password='df54ZR459',
        database='IrmaDB_result')

    curs = tuxmlDB.cursor(buffered=True)
    curs.execute(query)

    try: #Unflolding data
        result = curs.fetchall()
        if len(result) == 1:
            result = result[0]
        if len(result) == 1:
            result = result[0]
        return result
    except:
        return None

__queriesCache = {}
__totalFetchCount = 0 # <-- Deprecated
__incrementLocker = threading.Lock() # <-- Deprecated
__cacheLocker = threading.Lock()
__currentCompilationCount = 0

'''

Increments the global counter of requests.

Deprecated : The frequency-based refresh strategy is not relevant anymore

'''
def __incrementCounter():
    global __totalFetchCount
    __incrementLocker.acquire()
    __totalFetchCount += 1
    __incrementLocker.release()


'''

Function created in order to manage cache updates while avoiding race conditions.

'''
def __updateCache(query, data, isPassiveData):
    global __queriesCache
    cacheItem = __queriesCache.get(query, __CacheItem(passiveData=isPassiveData))
    cacheItem.update(data)
    __cacheLocker.acquire()
    __queriesCache[query] = cacheItem
    __cacheLocker.release()

'''

This function manages the cache's automatic refresh and purge.

Variables have been created in order simplify parameters modification. Please use them instead of "hard coding".

'''
def __refreshCacheRoutine(): # Works as a thread

    #Parameters

    waitingTimeBetweenRefreshes = 300

    timeToLive = 86400 #Cache items older than x seconds will be deleted during the next purge
    refreshCountForPurge = 188 #Each x refreshes, a purge will happen

    timeToLivePassiveItems = 86400 #Passive cache items older than x seconds will be deleted during the next purge
    refreshCountForPassiveItemsPurge = 752 #Each x refreshes, a purge of passive cache items will happen


    #Actual code

    global __queriesCache
    global __totalFetchCount
    global __currentCompilationCount
    refreshCount = 0
    while True:
        refreshCount +=1
        __cacheLocker.acquire()
        newCount = makeRequest("SELECT COUNT(cid) FROM compilations", caching=False)
        if newCount > __currentCompilationCount:
            __currentCompilationCount = newCount
            for request,cachedData in __queriesCache.items():
                if not cachedData.isPassiveData:
                    cachedData.update(__fetchData(request),impact=False)

        if refreshCount % refreshCountForPurge == 0: #Purge of unused cache items
            purgedQueriesCache = {}
            purgedFetchCount = 0 # <-- Deprecated
            for request,cachedData in __queriesCache.items():
                if (arrow.now() - cachedData.lastUpdate).seconds > timeToLive and not cachedData.isPassiveData:
                    purgedQueriesCache[request] = cachedData
                    purgedFetchCount += cachedData.useCount # <-- Deprecated
            __queriesCache = purgedQueriesCache
            __totalFetchCount = purgedFetchCount

        if refreshCount % refreshCountForPassiveItemsPurge == 0: #Purge of unused cache passive items
            purgedQueriesCache = {}
            purgedFetchCount = 0 # <-- Deprecated
            for request,cachedData in __queriesCache.items():
                if (arrow.now() - cachedData.lastUpdate).seconds > timeToLivePassiveItems and cachedData.isPassiveData:
                    purgedQueriesCache[request] = cachedData
                    purgedFetchCount += cachedData.useCount # <-- Deprecated
            __queriesCache = purgedQueriesCache
            __totalFetchCount = purgedFetchCount

        __cacheLocker.release()
        sleep(waitingTimeBetweenRefreshes)


'''

The core function of this file. 

Manages queries and cache interactions when requested.

Cache updates are made in a separate thread to avoid being stuck because of a cache refresh.
One thread per item to be updated in the cache. Behavior subject to change (In order to avoid thread creation cost).

'''
def makeRequest(query, caching = True, isPassiveData = False):
    if caching : #We check the cache
        __incrementCounter()
        try:
            return __queriesCache[query].getData()
        except Exception as e :
            pass
    data = __fetchData(query)
    if caching : #We update the cache
        updateThread = threading.Thread(target=__updateCache, args=(query, data, isPassiveData))
        updateThread.start()
    return(data)

__x = threading.Thread(target=__refreshCacheRoutine)
__x.start()





#Sample functions, each ones are described in README.md

def getCompilationCount(specificVersion = None):
    if specificVersion is None or 'All' in specificVersion:
        return makeRequest("SELECT COUNT(cid) FROM compilations")
    else:
        return makeRequest(f"SELECT COUNT(cid) FROM compilations WHERE compiled_kernel_version = '{specificVersion}'")

def compilationExists(compilationId):
    try:
        return bool(makeRequest(f"SELECT COUNT(cid) FROM compilations WHERE cid = '{compilationId}'"))
    except:
        return False

def compilationExistsAdvanced(table, column, value):
    #print(type(makeRequest(f"SELECT {column} FROM {table} WHERE {column} = {value} LIMIT 1")).__name__, file=sys.stderr)
    #print(makeRequest(f"SELECT {column} FROM {table} WHERE {column} = {value} LIMIT 1"), file=sys.stderr)
    #print(value, file=sys.stderr)
    #print(bool(makeRequest(f"SELECT {column} FROM {table} WHERE {column} = {value} LIMIT 1")==value), file=sys.stderr)
    #print(bool("\""+result+"\"" == value), file=sys.stderr)

    request = f"SELECT {column} FROM {table} WHERE {column} = {value} LIMIT 1"
    result = makeRequest(request)
    try:
        return bool("\""+result+"\"" == value)
    except:
        return False

def getCompilationInfo(compilationId, basic = False):
    class compilationInfo:
        def __init__ (self,compilationInfo,softwareInfo, hardwareInfo) :
            self.compilationInfo = compilationInfo
            self.softwareInfo = softwareInfo
            self.hardwareInfo = hardwareInfo
    try:
        comp = makeRequest("SELECT * FROM compilations WHERE cid = " + str(compilationId), isPassiveData=True)
        if not basic :
            soft = makeRequest("SELECT * FROM software_environment WHERE sid = " + str(comp[12]), isPassiveData=True)
            hard = makeRequest("SELECT * FROM hardware_environment WHERE hid = " + str(comp[13]), isPassiveData=True)
        return compilationInfo(comp,soft,hard)
    except:
        return None

def getCompilationFile(compilationId, requestedFileType):
    reqparam = None
    if requestedFileType == "config":
        reqparam="config_file"
    elif requestedFileType == "stdout":
        reqparam = "stdout_log_file"
    elif requestedFileType == "stderr":
        reqparam = "stderr_log_file"
    elif requestedFileType == "userOutput":
        reqparam = "user_output_file"
    try:
        return bz2.decompress(programmaticRequest(getColumn=reqparam, withConditions=f"cid = {compilationId}", caching= False, execute=True))
    except:
        return None

def getColumnsForCompilationsTable(includeBlobs = False):
    col = makeRequest("SHOW COLUMNS FROM `compilations`", isPassiveData=True)
    result = []
    for c in col:
        if includeBlobs :
            result.append(c[0])
        elif "blob" not in c[1]:
            result.append(c[0])
    return result

def getColumnsForHardwareEnvTable():
    col = makeRequest("SHOW COLUMNS FROM `hardware_environment`", isPassiveData=True)
    result = []
    for c in col:
            result.append(c[0])
    return result

def getColumnsForSoftwareEnvTable():
    col = makeRequest("SHOW COLUMNS FROM `software_environment`", isPassiveData=True)
    result = []
    for c in col:
            result.append(c[0])
    return result

def getExistingKernelVersions(desc = False):
    return makeRequest("SELECT DISTINCT compiled_kernel_version FROM compilations ORDER BY compiled_kernel_version " + ("DESC" if desc else "ASC"), isPassiveData=True)

def getNumberOfActiveOptions(compilationId):
    try:
        configFile = getCompilationFile(compilationId,"config")
        ny = 0
        for l in configFile.splitlines():
            if l.endswith("=y"):
                ny = ny + 1
        return ny
    except Exception as e:
        print(str(e), "\n" + "Unable to decompress... ", file=sys.stderr)
        return None

def programmaticRequest(getColumn=None, withConditions=None, ordering=None, limit:int=None, offset:int=None, mainTable='compilations comp',isPassiveData = False, useORConditionalOperator = False, caching=True, execute=False):
    options = ''

    softenv = False
    hardenv = False

    if getColumn is None:
        softenv = True
        hardenv = True
        getColumn = "*"

    for col in getColumnsForSoftwareEnvTable():
        if col in getColumn or col in withConditions:
            softenv = True
    
    for col in getColumnsForHardwareEnvTable():
        if col in getColumn or col in withConditions:
            hardenv = True

    if hardenv:
        mainTable += " JOIN hardware_environment hardenv ON comp.hid = hardenv.hid"
    if softenv:
        mainTable += " JOIN software_environment softenv ON comp.sid = softenv.sid"

    if not isinstance(getColumn, str): #If necessary, we reformat the columns input
        getColumn = ", ".join(getColumn)


    if withConditions is not None:
        if not isinstance(withConditions, str):  #If necessary, we reformat the conditions input
            withConditions = f" {'AND' if not(useORConditionalOperator) else 'OR'} ".join(withConditions)
        if len(withConditions) > 0: # If we effectively have an input, we add the "introduction"
            withConditions = " WHERE " + withConditions
        options += withConditions


    if ordering is not None:
        if not isinstance(ordering, str):  #If necessary, we reformat the ordering input
            ordering = ", ".join(ordering)
        if len(ordering) > 0: # If we effectively have an input, we add the "introduction"
            ordering = " ORDER BY "+ordering
        options += ordering

    if limit is not None:
        options += f" LIMIT {limit}"

    if offset is not None:
        options += f" OFFSET {offset}"

    query = f"SELECT {getColumn} FROM {mainTable}{options};"

    if execute:
        return makeRequest(query, isPassiveData=isPassiveData, caching=caching)
    else:
        return query
