#!/usr/bin/python3
import os
import sys
import matplotlib.pyplot as plt

from dbRequest import *


#Import dbManager
sys.path.insert(0, "..")
try:
    from dbManager import *
except ImportError:
    print('No Import')



    


#Choix de la version à télécharger
def getKernelSizeVersionList(versionKernel):
    versionKernel = "'" + versionKernel + "'"
    query = "SELECT compiled_kernel_size FROM compilations WHERE compiled_kernel_version=" + versionKernel + ";"

    _kernelSizeVersionList = read_query(query)
    data = []
    for e in _kernelSizeVersionList:
        for i in e:
            data.append(i)
    data = sorted(data)
    
    rounddata = []
    for e in data:
        if e != -1:
            i = '{:.2f}'.format(round(e/1000000, 2))
            rounddata.append(i)
        else:
            rounddata.append(e)
    
    return rounddata




def showHist(versionKernel):
    plt.hist(getKernelSizeVersionList(versionKernel))

    plt.title('kernel size distribution', fontsize=10)
    plt.xlabel('Mo')
    
    plt.show()
    



