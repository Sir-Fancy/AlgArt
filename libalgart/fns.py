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

sys.path.append("..")

# IMPLEMENT THIS
# ~  RAND(a, b)  Return integer between 'a' and 'b'
# ~  RANDF(a, b) Return float between 'a' and 'b' (discouraged for anything other than RANDF(0, 1))
# ~  FUZZ(a, b)  Return 'a', increased or decreased up to a maximum of 'b' (this is an easy way to add "fuzz" to your Algart)

class Fns(object):
    def __init__(self, p):
        self.defs = {"FAC" : factorial,
                     "SIN" : np.sin,
                     "COS" : np.cos,
                     "TAN" : np.tan,
                     "SINH": np.sinh,
                     "COSH": np.cosh,
                     "TANH": np.tanh,
                     "ABS" : np.absolute,
                     "SQRT": np.sqrt,
                     "GET" : self.get }
        
    def get(self, a):
        