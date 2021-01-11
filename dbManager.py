import bz2
import sys
import threading
from os import path
from time import sleep
import mysql.connector
import arrow

class __CacheItem:
    def __init__(self):
        self.__lock = threading.Lock()
        self.lastUpdate = arrow.now()
        self.useCount = 0
    def update(self, data):
        self.__lock.acquire()
        self.__data = data
        self.useCount += 1
        self.lastUpdate = arrow.now()
        self.__lock.release()
    def getData(self):
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

def __incrementCounter():
    global __totalFetchCount
    __incrementLocker.acquire()
    __totalFetchCount += 1
    __incrementLocker.release()

def __updateCache(query, data, queriesCache = __queriesCache):
    cacheItem = queriesCache.get(query, __CacheItem())
    cacheItem.update(data)
    __cacheLocker.acquire()
    queriesCache[query] = cacheItem
    __cacheLocker.release()

def __refreshCacheRoutine(queriesCache = __queriesCache): # Works as a thread
    global __totalFetchCount
    refreshCount = 0
    while True:
        refreshCount +=1
        __cacheLocker.acquire()
        for request,cachedData in queriesCache.items():
            if ((cachedData.useCount / __totalFetchCount) > 0.5)\
            or ((cachedData.useCount / __totalFetchCount) > 0.25 and (refreshCount % 4) == 0)\
            or ((cachedData.useCount / __totalFetchCount) > 0.125 and (refreshCount % 6) == 0)\
            or ((refreshCount % 10) == 0):
                cachedData.update(__fetchData(request))
        __cacheLocker.release()
        sleep(300)

def makeRequest(query, caching = True):
    if caching :
        __incrementCounter()
        try:
            return __queriesCache[query].getData()
        except:
            pass
    data = __fetchData(query)
    if caching :
        updateThread = threading.Thread(target=__updateCache, args=(query, data))
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
        comp = makeRequest("SELECT * FROM compilations WHERE cid = " + str(compilationId), caching=False)
        if not basic :
            soft = makeRequest("SELECT * FROM software_environment WHERE sid = " + str(comp[12]))
            hard = makeRequest("SELECT * FROM hardware_environment WHERE hid = " + str(comp[13]))
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