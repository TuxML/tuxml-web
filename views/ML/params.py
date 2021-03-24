import numpy as np

def getParam(line):
    param = ""
    eg = 0
    for char in line :
        if char == " ":
            continue
        elif char == "#":
            param = ""
            break
        elif char == "=":
            eg = 1
            break
        else:
            param = param + char
    if eg != 1:
        param = ""
    return param
        
     
def getParamTrue(line):
    param = ""
    eg = 0
    for char in line :
        if eg != 1:
            if char == " ":
                continue
            elif char == "#":
                param = ""
                break
            elif char == "=":
                eg = 1
                continue
            else:
                param = param + char
        else :
            if char == "y":
                return param
            else :
                return ""
    return ""
        
                
def file_len(fname):
    f = open(fname, "r")
    for i, l in enumerate(f):
        pass
    f.close()
    return i + 1


#if config_param exist in fname, return 1, else return 0
def existParam(fname, config_param):
    f = open(fname, "r")
    for l in f:
        
        l = l.rstrip('\n')
        if l == config_param:
            f.close()
            return 1
    f.close()
    return 0
        
      
def getPos(fname, paramTrue):
    f = open(fname, "r")
    for i, l in enumerate(f):
        l = l.rstrip('\n')
        if l == paramTrue:
            f.close()
            return i
        
    f.close()
    return -1



