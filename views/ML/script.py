#!/usr/bin/python3

import os
import sys
import numpy as np

from .getConfigFile import getConfig
from .growML import grow

version = "4.15"
number = 1000


for i in range(number):
    getConfig(version)
    grow(version)


    




