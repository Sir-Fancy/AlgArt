#!/usr/bin/env python
#
#  parser.py
#  Where the magic happens
# 
#
# Zack Marotta  (c)
import PIL
import numpy as np
from collections import OrderedDict
from user import *

class Parser:
    
    
    def __init__(self, width, height, depth, alg, verbose):
        self.width = width
        self.height = height
        self.depth = depth
        self.alg = alg
        self.verbose = verbose
        self.linedefs = OrderedDict()
        self.constants = {"MVAL": np.exp2(depth)-1, "ROWS": height, "COLS": width, "MAX": width*height}
        self.optvars = {"X", "Y", "P"}
        self.locals = []
        
        self.ops = {"=": self._assign,
                    "+": self._add,
                    "-": self._subtract,
                    "*": self._multiply,
                    "/": self._divide,
                    }
        self.setReqvars()
        
    def setReqvars(self):
        pass
        
    def crunch(self):
        ws = self.alg.replace("\n", ";").split(";") #lines with leading and/or trailing whitespace
        lines = map(lambda x: x.strip(), ws)
        for linenum, l in enumerate(lines): #iterate over line_number and full line
            if l == "": continue
            lsplit = l.split() # ['k', '=', 'x']
            if "=" not in lsplit:
                if lsplit[1] != "==":
                    missing("=", linenum, l, len(lsplit[0]))
                else:
                    missing("=", linenum, l, len(lsplit[0]), tip=1) #just a friendly reminder for all you fellow programmers ;)
            if lsplit[-1:] == "=":
                missing("expression", linenum, l, len(l)+1)
            #for index, op in enumerate(lsplit): #iterate over index and each character
            #    if op not in ops:
            #        self.locals.append(op)
            #    else:
            #        self.ops[op](lsplit[index-1], lsplit[index+1]) #send the appropriate ops method both operands
                
            #print l, line, line[0], line[2:]
            #self.linedefs[lsplit[0]] = lsplit[2:]
    
    
    
    def _assign(self):
        pass
    
    def _add(self):
        pass
    
    def _subtract(self):
        pass
    
    def _multiply(self):
        pass
    
    def _divide(self):
        pass
    
        
    def setreqvars(self):
        pass


class ParserGray(Parser):
    def setReqvars(self):
        self.reqvars = ("K")
    
class ParserRGB(Parser):
    def setReqvars(self):
        self.reqvars = ("K")

class ParserHSL(Parser):
    def setReqvars(self):
        self.reqvars = ("K")

class ParserHSV(Parser):
    def setReqvars(self):
        self.reqvars = ("K")
        
class ParserCYMK(Parser):
    def setReqvars(self):
        self.reqvars = ("K")