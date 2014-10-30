#!/usr/bin/env python
#
#  ops.py
#  class containing all operations
# 
#
# Zack Marotta  (c)

import numpy as np

class Ops:
    def __init__(self):
        self.defs = {"+" : np.add,
                     "-" : np.subtract,
                     "*" : np.multiply,
                     "/" : np.true_divide,
                     "^" : np.power,
                     "%" : np.mod,
                     "<<": np.left_shift,
                     ">>": np.right_shift,
                     "~" : np.invert,
                     "&&": np.bitwise_and,
                     "||": np.bitwise_or,
                     "X||":np.bitwise_xor,
                     "AND":np.logical_and,
                     "OR": np.logical_or,
                     "XOR":np.logical_xor,
                     "NOT":np.logical_not,
                     ">" : np.greater,
                     ">=": np.greater_equal,
                     "<" : np.less,
                     "<=": np.less_equal,
                     "==": np.equal }