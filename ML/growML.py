import os
import numpy as np
import sys
import shutil

from getConfigFile import getConfig
from params import *
from dbRequest import *
from sklearn.neighbors import KNeighborsClassifier



def growX(_version, files):


    
    """
    params file
    
    """

    #Fill file params with all params
    for cid_repo in files:
        path = cid_repo + "/config_file"


        params = open("../params", "a+")
        f = open(path, "r")

        for line in f:
            config_param = getParam(line)

            if config_param != "":
                if existParam("../params",config_param) == 0:
                    params.write(config_param + "\r\n")
        f.close()                     


    """
    X.npy
    
    """


    #get the position of the param from config_file in the params file
    #do it for all config_file and fill data with
    
    len_params = file_len("../params")

    if os.path.exists("../X.npy"):
        X = np.load("../X.npy")
        num_rows, num_cols = X.shape
        diffCols = len_params - num_cols
        if diffCols > 0:
            data = np.zeros((num_rows,len_params),dtype=np.int64)
            data[:,:-diffCols] = X
        else:
            data = X
    else:
        data = np.zeros(len_params,dtype=np.int64)
        data = data.reshape(1,len_params)



    for cid_repo in files:
        row = np.zeros(len_params,dtype=np.int64)
        path = cid_repo + "/config_file"

        f = open(path, "r")
        for line in f:
            paramTrue = getParamTrue(line)
            if paramTrue != "" :
                index = getPos("../params",paramTrue)
                row[index] = 1

        f.close()
        row = row.reshape(1,len_params)
        data = np.concatenate((data, row))



    if os.path.exists("../X.npy"):
        pass
    else:
        data = np.delete(data, 0, 0)
    
    
    np.save("../X.npy", data)
    
    
    
    
    

    
    

    
    
def growY(_version,files):
    
    
    #if cid_repo compile then set 1 to the position in the matrix
    if os.path.exists("../y.npy"):
        y_load = np.load("../y.npy")
        
    compilation_y = np.zeros(len(files),dtype=np.int64)

    for i, cid_repo in enumerate(files):
        query = "SELECT compiled_kernel_size FROM compilations WHERE cid = " + cid_repo + ";"
        size = read_query(query)
        size = size[0]
        size = size[0]
        if size != -1:
            compilation_y[i] = 1
            
    if os.path.exists("../y.npy"):
        y = np.concatenate((y_load,compilation_y))
    else:
        y = compilation_y
        
    np.save("../y.npy",y)
            



#use growX and growY and remove configs folder after
def grow(_version):
    pathConfigs = f"./{_version}/configs"

    try:
        os.chdir(pathConfigs)
    except OSError:
        print ("Failure Change current working directory to : %s " % pathConfigs)
        sys.exit()


    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory


    growX(_version, files)
    growY(_version, files)
        
    os.chdir("..")
    
    if os.path.exists("configs"):
        shutil.rmtree("configs")
    
    os.chdir("..")




#get the position of the param from the target config_file and fill x with    
def get_x(targetConfigFile, fparams):
    len_params = file_len(fparams)
    row = np.zeros(len_params,dtype=np.int64)


    f = open(targetConfigFile, "r")
    for line in f:
        paramTrue = getParamTrue(line)
        if paramTrue != "" :
            index = getPos(fparams,paramTrue)
            if index != -1:
                row[index] = 1

    f.close()
    return row.reshape(1,len_params)
    
 
    
    

    
    
    
    
    
def useKNC(X,y,x):
    
    print("y : " , y)
    
    print("X shape : " , X.shape)
    print("y shape : " , y.shape)
    print("x shape : " , x.shape)
    
    print("")
    
    #Use KNeighborsClassifier model
    model = KNeighborsClassifier()

    model.fit(X,y)

    model.score(X,y)

    
    prediction = model.predict(x)
    prediction = prediction[0]
    
    print("Predict_proba : " , model.predict_proba(x))
    print("Prediction : " , prediction)
    
    
    
    
    
    
    
    
    
    """


if len(sys.argv) != 5:
    print("Incorrect number of arguments")
    print("Usage : python3 predictCompilation.py _directory _version _numberOfFiles _targetConfigFile")
else :
    prediction(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    
    """