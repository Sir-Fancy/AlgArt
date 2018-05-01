#!/usr/bin/env python
#
#  fns.py
#  class containing all functions
# 
#
# Zack Marotta  (c)
import numpy as np
import sys
from math import factorial
import random

sys.path.append("..")

class Fns(object):
    def __init__(self):
        self.defs = {"FAC" : factorial,
                     "SIN" : np.sin,
                     "COS" : np.cos,
                     "TAN" : np.tan,
                     "SINH": np.sinh,
                     "COSH": np.cosh,
                     "TANH": np.tanh,
                     "ABS" : np.absolute,
                     "SQRT": np.sqrt,
                     "LOG" : np.log10,
                     "LN"  : np.log,
                     "RAND": lambda x: np.random.random()}