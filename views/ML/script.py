#!/usr/bin/python3

import os
import sys
import numpy as np

from .getConfigFile import getConfig
from .growML import grow
from .dbRequest import read_query



#number of compilations we want to download for each version
number = 10

_versionQuery = read_query("SELECT DISTINCT compiled_kernel_version FROM compilations;")
_allVersion = [ver[0] for ver in _versionQuery]


for version in _allVersion:
    for i in range(number):
        getConfig(version)
        grow(version)



    




