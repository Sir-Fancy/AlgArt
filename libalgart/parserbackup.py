#!/usr/bin/env python
#
#  parser.py
#  Where the magic happens
# 
#
# Zack Marotta  (c)
from PIL import Image, ImageDraw
import numpy as np
import colorsys
from collections import OrderedDict
from user import *
from libpyparsing.pyparsing import *

#The few functions below were taken from fourFn.py and SimpleCalc.py in the examples of the pyparsing lib.
#I have commented out some of the lines and modified others. The original files can be found at the following links:
#http://pyparsing.wikispaces.com/file/view/fourFn.py/30154950/fourFn.py
#http://pyparsing.wikispaces.com/file/view/SimpleCalc.py/30112812/SimpleCalc.py

exprStack = []

def pushFirst( strg, loc, toks ):
    exprStack.append( toks[0] )
def pushUMinus( strg, loc, toks ):
    for t in toks:
      if t == '-': 
        exprStack.append( 'unary -' )
      else:
        break

bnf = None
def BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        point = Literal( "." )
        #~ fnumber = Combine( Word( "+-"+nums, nums ) + 
                           #~ Optional( point + Optional( Word( nums ) ) ) +
                           #~ Optional( e + Word( "+-"+nums, nums ) ) )
        #fnumber = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
        fnumber = Regex(r"[+-]?\d+(:?\.\d*)?") #disabled sci notation because I'd rather things didn't get messy
        ident = Word(alphas, alphas+nums+"_$")
     
        plus  = Literal("+")
        minus = Literal("-")
        mult  = Literal("*")
        div   = Literal("/")
        lpar  = Literal("(").suppress()
        rpar  = Literal(")").suppress()
        addop  = plus | minus
        multop = mult | div
        expop = Literal("^")
        
        expr = Forward()
        atom = ((0,None)*minus + (fnumber | ident + lpar + expr + rpar | ident).setParseAction(pushFirst) | 
                Group(lpar + expr + rpar)).setParseAction(pushUMinus) 
        
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))
        #Where PEMDAS takes place
        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
        bnf = expr
    return bnf

ops = { "+" : np.add,
        "-" : np.subtract,
        "*" : np.multiply,
        "/" : np.divide,
        "^" : np.power }
fn  = { "sin" : np.sin,
        "cos" : np.cos,
        "tan" : np.tan,
        "abs" : np.absolute }
def evaluateStack(s):
    print "stack:", s
    op = s.pop()
    if op == 'unary -':
        return -evaluateStack(s)
    if op in ops:
        op2 = evaluateStack(s)
        op1 = evaluateStack(s)
        return ops[op]( op1, op2 )
    elif op in fn:
        return fn[op](evaluateStack(s))
    elif op[0].isalpha():
        raise Exception("invalid identifier '%s'" % op)
    else:
        return float(op)

#Uncomment below for debugging this file
#if __name__ == "__main__":
#    import sys
#    def test(s):
#        global exprStack
#        exprStack = []
#        try:
#            results = BNF().parseString( s, parseAll=True )
#            val = evaluateStack( exprStack[:] )
#        except ParseException as e:
#            print(s, "failed parse:", str(e))
#        except Exception as e:
#            print(s, "failed eval:", str(e))
#        else:
#            print val
#    test(sys.argv[1])
    
class Parser:
    def __init__(self, width, height, depth, alg, verbose, fg, bg, filename):
        self.width = width
        self.height = height
        self.depth = depth
        self.alg = alg
        self.verbose = verbose
        self.filename = filename
        #self.linedefs = OrderedDict()
        if fg is not None:
            fghue = colorsys.hsv_to_rgb(self.fg)
        else:
            fghue = colorsys.hsv_to_rgb(0, 0, 1)
            
        self.constants = {"MVAL": np.exp2(depth)-1, "ROWS": height, "COLS": width, "MAX": width*height}
        self.optvars = {"X", "Y", "P"}
        self.local = []
        self.localfns = []
        self.ops = {"+": np.add,
                    "-": np.subtract,
                    "*": np.multiply,
                    "/": np.divide,
                    "^": np.power}
        self.fns = {"sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,
                    "abs": np.absolute}
        self.newImage(depth)
        
    def crunch(self):
        #global exprStack
        exprStack = []
        ws = self.alg.replace("\n", ";").split(";") #lines with leading and/or trailing whitespace
        lines = map(lambda x: x.strip(), ws)
        
        for currentRow in xrange(self.height):
            # 1111
            # 2222
            # 3333
            for currentCol in xrange(self.width):
                # 1234
                # 1234
                # 1234
                for input_string in lines:
                    del exprStack[:]
                    if input_string != '':
                        if self.verbose: verbose(input_string)
                        try:
                            L=pattern.parseString(input_string, parseAll=True)
                        except ParseException as pe:
                            L=['Parse Failure',input_string]
                      
                      # show result of parsing the input string
                        if self.verbose: print(input_string, "->", L)
                        if len(L)==0 or L[0] != 'Parse Failure':
                            if self.verbose: verbose("exprStack=", exprStack)
                        
                        # calculate result , store a copy in ans , display the result to user
                            try:
                                result=evaluateStack(exprStack)
                            except Exception as e:
                                err(str(e))
                            else:
                                variables['ans']=result
                                self.placePixel(currentRow, currentCol, val)
                      
                            # Assign result to a variable if required
                            if L.varname:
                                variables[L.varname] = result
                            if debug_flag: print("variables=",variables)
                        else:
                            err("ParseFailure: Line ", more=True)
                            err(pe.line, more=True)
                            err(" "*(pe.column-1) + "^", more=True)
                            err(pe)
              
                    
        
    def newImage(self):
        pass
    
    def placePixel(self):
        pass
    
    def saveImage(self):
        self.im.save(self.filename, "png")
    

#http://effbot.org/imagingbook/imagedraw.htm

class ParserGray(Parser):
    def newImage(self):
        self.reqvars = ("K")
        self.im = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)

            
    def placePixel(self, x, y, k):
            
            
        color = 
        self.draw.point((x, y), fill=k)
    
class ParserRGB(Parser):
    def newImage(self, depth):
        self.reqvars = ("R", "G", "B")
        self.im = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)
    
    def placePixel(self, r, g, b):
        

class ParserHSL(Parser):
    def newImage(self, depth):
        self.reqvars = ("H", "L", "S")
        self.im = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)

    def placePixel(self, h, l, s):
        
    
class ParserHSV(Parser):
    def newImage(self, depth):
        self.reqvars = ("H", "S", "V")
        self.im = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)
    
    def placePixel(self, h, s, v):
        

class ParserCYMK(Parser):
    def newImage(self, depth):
        self.reqvars = ("C", "Y", "M", "K")
        self.im = Image.new("CYMK", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)
    
    def placePixel(self, c, y, m, k):
        

#Make a pull request if you want to add more modes!
