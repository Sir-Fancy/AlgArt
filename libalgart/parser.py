#!/usr/bin/env python
#
#  parser.py
#  Where the magic happens
# 
#
# Zack Marotta  (c)
from PIL import Image#, ImageDraw
import numpy as np
import random as rnd
import colorsys
#from collections import OrderedDict

from user import *
from ops import Ops
from fns import Fns

from libpyparsing.pyparsing import *  #TODO: import only what I need

#The few functions below were taken from fourFn.py and SimpleCalc.py in the examples of the pyparsing lib.
#I have commented out some of the lines and modified others. The original files can be found at the following links:
#http://pyparsing.wikispaces.com/file/view/fourFn.py/30154950/fourFn.py
#http://pyparsing.wikispaces.com/file/view/SimpleCalc.py/30112812/SimpleCalc.py


log = Log() #required for numpy exceptions
np.seterrcall(log)
np.seterr(all="log")
#ParserElement.enablePackrat() #WARNING: MIGHT BREAK STUFF


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
        #ident = Word(alphas, alphas+nums+"_$")
        ident = Word(alphas, alphas+nums)
        
        plus  = Literal("+")
        minus = Literal("-")
        mult  = Literal("*")
        div   = Literal("/") | Literal("%")
        lpar  = Literal("(").suppress()
        rpar  = Literal(")").suppress()
        addop  = plus | minus
        miscop = Keyword("<<") | Keyword(">>") | Keyword("~") | Keyword("&&") | Keyword("X||") | Keyword("||") | Keyword("AND") | Keyword("XOR") | Keyword("OR") | Keyword("NOT") | Keyword(">=") | Keyword(">") | Keyword("<=") | Keyword("<") | Keyword("==")
        multop = mult | div | miscop
        
        expop = Literal("^")
        
        expr = Forward()
        atom = ((0,None)*minus + (fnumber | ident + lpar + expr + rpar | ident).setParseAction(pushFirst) | 
                Group(lpar + expr + rpar)).setParseAction(pushUMinus) # Todo: Find out how the fuck this recursive stuff works
        
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))
        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
        bnf = expr
    return bnf

arithExpr = BNF()
ident = Word(alphas).setName("identifier")
assignment = ident("varname") + '=' + arithExpr
comment = Literal("#") + restOfLine
#pattern = assignment
pattern = assignment + Optional(comment)
    
class Parser(object):
    def __init__(self, isclamp, width, height, alg, verbose, debug, fg, bg, filename):
        self.isclamp = isclamp
        self.width = width
        self.height = height
        self.bands = 1
        self.alg = alg
        self.verbose = verbose
        self.debug = debug
        self.filename = filename
        if fg is not None:
            self.fghue = colorsys.hls_to_rgb(fg[0]/360, fg[1], fg[2])
        else:
            self.fghue = colorsys.hls_to_rgb(0, 0, 1)
        if bg is not None:
            self.bghue = colorsys.hls_to_rgb(bg[0]/360, bg[1], bg[2])
        else:
            self.bghue = colorsys.hls_to_rgb(0, 0, 0)
        self.constants = {"ROWS": height, "COLS": width, "MAX": width*height}
        self.optvars = {"X": 0, "Y": 0, "P": 0}
        self.locals = {}
        self.ops = Ops()
        self.fns = Fns()

    
    def mainSequence(self):
        self.newImage()
        if self.verbose: vprint("Size:{}\tPixels:{}\tCustom fg/bg RGB color:({}, {})\nRequired variables: {}\nAlgorithm:\n{}\n".format("{}x{}".format(self.width, self.height), self.width*self.height, self.fghue, self.bghue, self.reqvars, self.alg))
        self.crunch()
        self.placePixels()
        self.saveImage()
    
    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':                        #negate
            return -self.evaluateStack(s)
        if op in self.ops.defs:                    #perform op
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.ops.defs[op](op1, op2)
        elif op in self.fns.defs:                  #perform fn
            return self.fns.defs[op](self.evaluateStack(s))
        elif op[0].isalpha():
            if op in self.optvars:
                return self.optvars[op]     #return optvar
            if op in self.locals:
                return self.locals[op]      #return local var
            if op in self.constants:
                return self.constants[op]   #return constant
            raise Exception("invalid identifier '%s'" % op)
        else:
            return float(op)
        
    def crunch(self):
        print("Parsing...")
        global exprStack
        exprStack = []
        self.pixeldata = np.ndarray(shape=(self.height, self.width, self.bands), dtype=float)
        maxp = self.constants["MAX"]
        ws = self.alg.replace("\n", ";").split(";") #lines with leading and/or trailing whitespace
        lines = map(lambda x: x.strip(), ws) #trims whitespace
        
        for currentRow in xrange(self.height):
            self.optvars["Y"] = currentRow
            # 1111
            # 2222
            # 3333
            for currentCol in xrange(self.width):
                self.optvars["X"] = currentCol
                pixval = []
                if self.verbose: progbar(self.optvars["P"], maxp)
                # 1234
                # 1234
                # 1234
                for i, input_string in enumerate(lines):
                    
                    if input_string != '':
                        del exprStack[:]
                    
                        ###  IMPLEMENT WHEN RANDOM FUNCTIONS ARRIVE
                        #isplit = input_string.split()
                        #if isplit[1] != "=":
                        #    if isplit[0][0] == "$":
                        #        try:
                        #            rand.seed(int(isplit[0][1:]))
                        #        except:
                        #            err("ParseFailure: Line 1\n{}\n ^ invalid seed value".format(input_string))
                        #    else:
                        #        missing("=", i, isplit)
                        ###

                        #if self.verbose: vprint(input_string + "\n")#
                        try:
                            L=pattern.parseString(input_string, parseAll=True) #EXECUTE MAGIC.EXE    seriously this shit is insane
                        except ParseException as pe:
                            L=['Parse Failure',input_string]
                      
                      # show result of parsing the input string
                        #if self.verbose: print(input_string, "->", L)#
                        if len(L)==0 or L[0] != 'Parse Failure':
                            #if self.verbose: vprint("exprStack = {}\n".format(exprStack))#
                            try:
                                result=self.evaluateStack(exprStack)
                            except Exception as e:
                                err(e)
                            else:
                                self.locals[L.varname] = result
                            #if self.verbose: vprint("variables = {}\n".format(variables))#
                        else:
                            err("ParseFailure: Line ",   more=True)
                            err(pe.line,                 more=True)
                            err(" "*(pe.column-1) + "^", more=True)
                            err(pe)
                    #end of current line
                for v in self.reqvars:
                    pixval.append(self.locals[v])                   #[255,255,255]
                self.pixeldata[currentCol, currentRow] = pixval          #[ ..., [255,255,255] ]
                self.optvars["P"] += 1
                #end of column
            #end of row
        #end of method
    
    def newImage(self):
        pass
    
    def convert(p): #this will be overridden to return an RGB/CYMK tuple
        pass
    
    def placePixels(self):
        print("Placing pixels...")
        maxp = self.constants["MAX"]
        if self.isclamp:
            self.maxpvalue = 255
            finaldata = clamp255(self.pixeldata)
        else:
            self.maxpvalue = np.amax(self.pixeldata)
            if self.verbose: vprint("Creative mode range: 0-{}\n".format(self.maxpvalue))
            finaldata = self.pixeldata
        i = 0
        for y in xrange(self.height):
            for x in xrange(self.width):
                if self.verbose: progbar(i, maxp)
                color = self.convert(finaldata[x,y])
                self.pix[x,y] = color
                i += 1
        if self.debug: self.saveDebug(self.pixeldata)

    
    def saveImage(self):
        self.im.save(self.filename, "png")
        print("Saving as {}".format(self.filename))
        
    
    def saveDebug(self, array):
        vprint("Saving debug data to debug.txt...\n")
        f = open("debug.txt", "w")
        for y in xrange(self.height):
            for x in xrange(self.width):
                for z in array[x,y]:
                    f.write(str(z))
                f.write(",")
            f.write("\n")
        f.close()
    

#http://effbot.org/imagingbook/imagedraw.htm

class ParserGray(Parser):
    def newImage(self):
        self.reqvars = ("K")
        self.bands = 1
        self.im = Image.new("RGB", (self.width, self.height))
        self.pix = self.im.load()

    def convert(self, p):
        r = lerp(self.bghue[0], self.fghue[0], p[0]/self.maxpvalue)*255 # linearinterpolate([0-1.0], [0-1.0], [0-255]/255)*255
        g = lerp(self.bghue[1], self.fghue[1], p[0]/self.maxpvalue)*255
        b = lerp(self.bghue[2], self.fghue[2], p[0]/self.maxpvalue)*255
        return (int(round(r)), int(round(g)), int(round(b)))

class ParserRGB(Parser):
    def newImage(self):
        err("NOT IMPLEMENTED")
        self.reqvars = ("R", "G", "B")
        self.bands = 3
        self.im = Image.new("RGB", (self.width, self.height))
        self.pix = self.im.load()
    
    def convert(self, p):
        return p

class ParserHLS(Parser):
    def newImage(self):
        err("NOT IMPLEMENTED")
        self.reqvars = ("H", "L", "S")
        self.bands = 3
        self.im = Image.new("RGB", (self.width, self.height))
        self.pix = self.im.load()

    def convert(self, p):
        return colorsys.hls_to_rgb(p[0]/255, p[1]/255, p[2]/255)
    
class ParserHSV(Parser):
    def newImage(self):
        err("NOT IMPLEMENTED")
        self.reqvars = ("H", "S", "V")
        self.bands = 3
        self.im = Image.new("RGB", (self.width, self.height))
        self.pix = self.im.load()

    def convert(self, p):
        return colorsys.hsv_to_rgb(p[0]/255, p[1]/255, p[2]/255)

class ParserCYMK(Parser):
    def newImage(self):
        err("NOT IMPLEMENTED")
        self.bands = 4
        self.reqvars = ("C", "Y", "M", "K")
        self.im = Image.new("CYMK", (self.width, self.height))
        self.pix = self.im.load()
    
    def convert(self, p):
        return p

class ParserYIQ(Parser):  #TODO
    def newImage(self):
        err("NOT IMPLEMENTED")
        self.reqvars = ("Y", "I", "Q")
        self.bands = 3
        self.im = Image.new("RGB", (self.width, self.height))
        self.pix = self.im.load()



#Make a pull request if you want to add more modes!
