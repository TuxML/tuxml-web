import os
import numpy as np
import sys

from getLogs import getLogs
from params import *
from dbRequest import *
from sklearn.neighbors import KNeighborsClassifier



def prediction(_directory, _version, _numberOfFiles, _targetConfigFile):
    getLogs(_directory,_version,_numberOfFiles)



    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory
    print("Files in %r: %s\n" % (cwd, files)) 
    
    print ("Data processing ...\n")



    #Fill file params with all params
    for cid_repo in files:
        path = cid_repo + "/config_file"


        params = open("params", "a+")
        f = open(path, "r")

        for line in f:
            config_param = getParam(line)

            if config_param != "":
                if existParam("params",config_param) == 0:
                    params.write(config_param + "\r\n")
        f.close()                     





    #get the position of the param from config_file in the params file
    #do it for all config_file and fill data with
    len_params = file_len("params")

    data = np.zeros(len_params,dtype=np.int64)

    for cid_repo in files:
        row = np.zeros(len_params,dtype=np.int64)
        path = cid_repo + "/config_file"

        f = open(path, "r")
        for line in f:
            paramTrue = getParamTrue(line)
            if paramTrue != "" :
                index = getPos("params",paramTrue)
                row[index] = 1

        f.close()
        data = np.concatenate((data, row))



    np.set_printoptions(threshold=sys.maxsize)

    data = data.reshape(len(files)+1,len_params)
    data = np.delete(data, 0, 0)


    #if cid_repo compile then set 1 to the position in the matrix
    compilation_y = np.zeros(len(files),dtype=np.int64)

    for i, cid_repo in enumerate(files):
        query = "SELECT compiled_kernel_size FROM compilations WHERE cid = " + cid_repo + ";"
        size = read_query(query)
        size = size[0]
        size = size[0]
        if size != -1:
            compilation_y[i] = 1


    #Use KNeighborsClassifier model
    model = KNeighborsClassifier()
    X = data
    y = compilation_y
    
    model.fit(X,y)

    model.score(X,y)


    #get the posidition of the param from the target config_file and fill x with    
    
    cwd = os.getcwd()  # Get the current working directory (cwd)
    
    _targetConfigFile = "../" + _targetConfigFile
    x = toPredict(_targetConfigFile,"params")
    
    print("y : " , y)
    
    print("X shape : " , X.shape)
    print("y shape : " , y.shape)
    print("x shape : " , x.shape)
    
    print("")
    
    prediction = model.predict(x)
    prediction = prediction[0]
    
    print("Predict_proba : " , model.predict_proba(x))
    print("Prediction : " , prediction)

    
    return prediction







if len(sys.argv) != 5:
    print("Incorrect number of arguments")
    print("Usage : python3 predictCompilation.py _directory _version _numberOfFiles _targetConfigFile")
else :
    prediction(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])