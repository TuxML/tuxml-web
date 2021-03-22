#!/usr/bin/python3
from getConfigFile import getConfig
from growML import grow
import os
import sys
import numpy as np


version = '4.15'
number = 1
path = "/home/zprojet/tuxml-web/ML"

try:
    os.chdir(path)
except OSError:
    print ("Failure Change current working directory to : %s " % path)
    sys.exit()

for i in range(number):
    getConfig(version)
    grow(version)


    




