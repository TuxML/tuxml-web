import bz2
import sys
import threading
from os import path
from time import sleep
import mysql.connector
import arrow

class __CacheItem:
    def __init__(self, passiveData = False):
        self.__lock = threading.Lock()
        self.lastUpdate = arrow.now()
        self.useCount = 0
        self.isPassiveData = passiveData
        self.__data = None
    def update(self, data, impact = True):
        self.__lock.acquire()
        self.__data = data
        if impact :
            self.useCount += 1
            self.lastUpdate = arrow.now()
        self.__lock.release()
    def getData(self):
        if self.isPassiveData:
            data = self.__data
            return data
        self.__lock.acquire()
        data = self.__data
        self.useCount += 1
        self.__lock.release()
        return data

def __fetchData(query):
    if (path.exists("tunnel")):
        tuxmlDB = mysql.connector.connect(
        host='localhost',
        port=20000,
        user='web',
        password='df54ZR459',
        database='IrmaDB_result')
    else:
        tuxmlDB = mysql.connector.connect(
        host='148.60.11.195',
        user='web',
        password='df54ZR459',
        database='IrmaDB_result')

    curs = tuxmlDB.cursor(buffered=True)
    curs.execute(query)
    try:
        result = curs.fetchall()
        if len(result) == 1:
            result = result[0]
        if len(result) == 1:
            result = result[0]
        return result
    except:
        return None

__queriesCache = {}
__totalFetchCount = 0
__incrementLocker = threading.Lock()
__cacheLocker = threading.Lock()
__currentCompilationCount = 0


def __incrementCounter():
    global __totalFetchCount
    __incrementLocker.acquire()
    __totalFetchCount += 1
    __incrementLocker.release()

def __updateCache(query, data, isPassiveData):
    global __queriesCache
    cacheItem = __queriesCache.get(query, __CacheItem(passiveData=isPassiveData))
    cacheItem.update(data)
    __cacheLocker.acquire()
    __queriesCache[query] = cacheItem
    __cacheLocker.release()

def __refreshCacheRoutine(): # Works as a thread
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

        if refreshCount % 188 == 0:
            purgedQueriesCache = {}
            purgedFetchCount = 0
            for request,cachedData in __queriesCache.items():
                if (arrow.now() - cachedData.lastUpdate).seconds > 86400 and not cachedData.isPassiveData:
                    purgedQueriesCache[request] = cachedData
                    purgedFetchCount += cachedData.useCount
            __queriesCache = purgedQueriesCache
            __totalFetchCount = purgedFetchCount

        if refreshCount % 752 == 0:
            purgedQueriesCache = {}
            purgedFetchCount = 0
            for request,cachedData in __queriesCache.items():
                if (arrow.now() - cachedData.lastUpdate).seconds > 86400 and cachedData.isPassiveData:
                    purgedQueriesCache[request] = cachedData
                    purgedFetchCount += cachedData.useCount
            __queriesCache = purgedQueriesCache
            __totalFetchCount = purgedFetchCount

        __cacheLocker.release()
        sleep(300)

def makeRequest(query, caching = True, isPassiveData = False):
    if caching :
        __incrementCounter()
        try:
            return __queriesCache[query].getData()
        except Exception as e :
            pass
    data = __fetchData(query)
    if caching :
        updateThread = threading.Thread(target=__updateCache, args=(query, data, isPassiveData))
        updateThread.start()
    return(data)

__x = threading.Thread(target=__refreshCacheRoutine)
__x.start()





#Sample functions

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
        return bz2.decompress(makeRequest(f"SELECT {reqparam} FROM compilations WHERE cid = {compilationId}", caching=False))
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
        return -1

