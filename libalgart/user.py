#!/usr/bin/env python
#
#  user.py
#  Useful system/type functions
# 
#
# Zack Marotta  (c)

import sys

def err(msg, s=None, pos=None, why=None, critical=True):
    print("\x1b[91;1m" + str(msg)+ "\x1b[0m")
    if critical:
        sys.exit(1)

def missing(char, linenum, line, pos, tip=None):
    """Return error that shows where something missing is needed.
        Format: missing(offending_character, line_number, line_string, index_of_missing_character)"""
    if tip == None:
        err("InvalidStatement: Missing {} on line {}\n{}\n{}".format(char, linenum + 1, line, " " * (pos+1) + "^" ))
    elif tip == 1:
        err("InvalidStatement: Missing {} on line {}\n{}\n{}\n(Did you mean \"=\"? ;-)".format(char, linenum + 1, line, " " * (pos+1) + "^" ))
    
def isNum(x):
    try:
        float(x)
        return True
    except ValueError:
        return False