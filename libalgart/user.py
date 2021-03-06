#!/usr/bin/env python
#
#  user.py
#  Useful system/type functions
# 
#
# Zack Marotta  (c)

from __future__ import division
from numpy import minimum, maximum, ma
import sys


def err(msg, more=False):
    """Print error in bold, bright red text. Optionally continue execution for further errors."""
    print("\x1b[91;1m" + str(msg)+ "\x1b[0m")
    if not more:
        sys.exit(1)

def vprint(msg):
    """Print a message in bold, bright yellow text for debugging in verbose mode."""
    sys.stderr.write("\x1b[93m" + str(msg) + "\x1b[0m")


def missing(char, linenum, line): #was used for any missing character, but that's now handled by pyparsing,
    tip = False                   #> so now it's adapted for missing "="s in assignments
    lstr = line.join(" ")
    pos = len(line)[0] + 1
    
    err("InvalidStatement: Missing '{}' on line {}\n{}\n{} expected '='".format(char, linenum + 1, lstr, " " * pos + "^" ), more=tip)
    if line[1] == "==": err("\n(Did you mean \"=\"? ;-)") #we've all done it :)
    sys.exit(1)
    
#def isNum(x): #legacy; probably won't be used anymore.    ...heh. It's funny I'm calling something legacy even before the first release.
#    """Check if x is a number."""
#    try:
#        float(x)
#        return True
#    except ValueError:
#        return False
    
def lerp(v0, v1, p):
    """Linear interpolation between tuples v0 and v1 with phase p"""
    return (1 - p) * v0 + p * v1

def clamp255(a):
    """Convenience function for clamping to 0-255"""
    #return maximum(0, minimum(a, 255))
    return ma.clip(a, 0, 255)

def progbar(p, f):
    """Display a progress bar between 0 and f with progress p in verbose"""
    pp = p + 1
    i = int(round((pp+1)/f * 60))
    vprint("\x1b[93m[{}{}] {} / {}\x1b[0m\r".format("="*i, " "*(60-i), pp, f))
    if pp == f:
        sys.stderr.write("\n")
        

class Log:
    def write(self, msg):
        err(msg)