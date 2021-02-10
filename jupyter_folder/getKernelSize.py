#!/usr/bin/python3
import os
import sys
from dbRequest import *


#Choix de la version à télécharger
def getKernelSizeVersionList(_versionSelect):
    _kernelSizeVersionList = read_query(f"SELECT compiled_kernel_size FROM compilations WHERE compiled_kernel_version={_versionSelect} ;")
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
    



