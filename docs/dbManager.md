# Queries library documentation
# "Smart caching" system
Behind this name is a simple way to keep data as fresh as possible without having to overwhelm the database with requests, as a complementary to flask-caching.

+ Every 5 minutes, the system will check if the compilations count has changed. And if so, the cache items will be refreshed.

+ Every 6 hours, the cache will be purged of items that haven't been used in 24 hours.

+ And every 24 hours, the cache will be purged of passiveData-flagged items that haven't been used in that period of time.

+ Cached items with the passiveData flag will never be refreshed so **use the flag wisely.**


# Methods
## makeRequest
```python
makeRequest(query, caching = True, isPassiveData = False)
```

If **caching** is set to False :

+ Makes a request to the database
+ Unfolds the result (up to two times) if necessary.

else :

+ Checks if the specified `query` already exists in the cache. And returns what's cached it if so.
+ If not, it makes a request, unfolds it, save it into the cache and returns it.


The `isPassiveData` option allows to create cache items with the passiveData flag, with the exact same impact than written above.

## getCompilationCount
```python
getCompilationCount(specificVersion = None)
```

Returns the number of compilation made for a specified kernel version.

If `specificVersion` is unspecified, or set to 'All', then the total number of compilations will be returned.

## compilationExists
```python
compilationExists(compilationId)
```

Returns if the specified compilation id exists or not.

## getCompilationInfo - To be rewritten (Returned object will change)
```python
getCompilationInfo(compilationId, basic = False)
```

Returns a `compilationInfo` object containing:
+ `compilationInfo.compilationInfo` : List containing informations about the requested configuration (compilation time, ...)
+ `compilationInfo.softwareInfo` : List containing informations about the software environment of the requested configuration
+ `compilationInfo.hardwareInfo` : List containing informations about the hardware environment of the requested configuration

The `basic` option returns the same object, but with `.softwareInfo` and `.hardwareInfo` set to None.

## getCompilationFile - To be updated (Needs more robustness)
```python
getCompilationFile(compilationId, requestedFileType)
```

Returns the file requested (specified with `requestedFileType`) for the compilation `compilationId`. Returns None if the file is broken or not found.

 `requestedFileType` can be `'config'`, `'stdout'`, `'stderr'` or `'userOutput'`
 
## getColumnsForCompilationsTable
```python
getColumnsForCompilationsTable(includeBlobs = False)
```

Utilitary option that returns a list of the columns of the 'compilations' table.
Set the `includeBlobs` option to True to get the blobs-containing columns as well.

## getColumnsForHardwareEnvTable
```python
getColumnsForhardwareEnvTable()
```

Utilitary option that returns a list of the columns of the 'hardware_environment' table.

## getColumnsForSoftwareEnvTable
```python
getColumnsForSoftwareEnvTable()
```

Utilitary option that returns a list of the columns of the 'software_environment' table.

## getExistingKernelVersions - To be updated (Param name)
```python
getExistingKernelVersions(desc = False)
```

Returns the list of the kernel versions that have been compiled in the database.
Set `desc` to true to invert the order of the list (From increasing ordre to decreasing).

## getNumberOfActiveOptions
```python
getNumberOfActiveOptions(compilationId)
```
Returns the number of active options for a specific `compilationId`.

## getSid
```python
getSid(system_kernel, system_kernel_version, linux_distribution, linux_distribution_version, gcc_version, libc_version, tuxml_version)
```
Get the existing sid for the specified software characteristics, returns `None` if there is no sid associated with this combination.

## getHid
```python
getHid(architecture, cpu_brand_name, number_cpu_core, cpu_max_frequency, ram_size, mechanical_disk)
```
Get the existing hid for the specified hardware characteristics, returns `None` if there is no hid associated with this combination.

## programmaticRequest
```python
programmaticRequest(getColumn="*", withConditions="", ordering=None, limit:int=None, offset:int=None, mainTable='compilations comp' ,isPassiveData = False, useORConditionalOperator = False, caching=True, execute=False)
```

Generates an SQL command from given parameters. Makes database requests far easier to write.

#### Main caracteristic of `getColumn`, `withConditions` and `ordering`:
They can accept arrays, and  also accept naturally-written lists (eg: `getColumn="sid,architecture"`)

#### About `caching`, `isPassiveData` and `execute`:
This method is capable to use the `makeRequest()` method.

By default, `execute` is set to False. Setting it to true will execute the generated command. 

The `caching` parameter is directly piped to the call to `makeRequest()`, same with `isPassiveData`.

#### "But what if I want to get columns located in the `software_environment` table ?"
Just put the column you want to get in the `getColumn`, the method automatically does the needed joining.

#### Example
##### Basic example
Calling the method with the following parameters
```python
programmaticRequest getColumn=['cid','architecture'], withConditions=['cid > 100000','cid < 100010'])
```

generates this command
```sql
SELECT cid, architecture FROM compilations comp JOIN hardware_environment hardenv ON comp.hid = hardenv.hid WHERE cid > 100000 AND cid <100010;
```

##### Highlighting the automatic selection of the needed table

Calling the method this way
```python
programmaticRequest(getColumn="architecture", withConditions="hid = 1")
```

generates this command
```sql
SELECT architecture FROM hardware_environment hardenv WHERE hid = 1;
```



#### Note 
The `mainTable` parameter is now considered as deprecated and will be removed in the future.
