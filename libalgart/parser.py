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
from collections import OrderedDict
from user import *
from libpyparsing.pyparsing import *  #TODO: import only what I need

#The few functions below were taken from fourFn.py and SimpleCalc.py in the examples of the pyparsing lib.
#I have commented out some of the lines and modified others. The original files can be found at the following links:
#http://pyparsing.wikispaces.com/file/view/fourFn.py/30154950/fourFn.py
#http://pyparsing.wikispaces.com/file/view/SimpleCalc.py/30112812/SimpleCalc.py

exprStack = []
#ParserElement.enablePackrat() #WARNING: MIGHT BREAK STUFF

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
        div   = Literal("/")
        lpar  = Literal("(").suppress()
        rpar  = Literal(")").suppress()
        addop  = plus | minus
        multop = mult | div
        expop = Literal("^")
        
        expr = Forward()
        atom = ((0,None)*minus + (fnumber | ident + lpar + expr + rpar | ident).setParseAction(pushFirst) | 
                Group(lpar + expr + rpar)).setParseAction(pushUMinus) 
        
        factor = Forward()                                                         #
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))    #
        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))    #
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))        # Todo: Find out how the fuck this recursive stuff works
        bnf = expr
    return bnf

arithExpr = BNF()
ident = Word(alphas).setName("identifier")
assignment = ident("varname") + '=' + arithExpr
comment = Literal("#") + restOfLine
#pattern = assignment
pattern = assignment + Optional(comment)

#comma = Literal(",").suppress()
#arguments = delimitedList(ident("argument"))
#function = ident + lpar + arguments + rpar 
#fnpattern = function + '=' + arithExpr  #This was originally going to allow functions in your equations, but I wanted to keep it more simple and not slow it down. Also it didn't work.

#ops = { "+" : np.add,
#        "-" : np.subtract,
#        "*" : np.multiply,
#        "/" : np.divide,
#        "^" : np.power }
#fn  = { "sin" : np.sin,
#        "cos" : np.cos,
#        "tan" : np.tan,
#        "abs" : np.absolute }
#def evaluateStack(s):
#    print "stack:", s
#    op = s.pop()
#    if op == 'unary -':
#        return -evaluateStack(s)
#    if op in ops:
#        op2 = evaluateStack(s)
#        op1 = evaluateStack(s)
#        return ops[op](op1, op2)
#    elif op in fn:
#        return fn[op](evaluateStack(s))
#    elif op[0].isalpha():
#        raise Exception("invalid identifier '%s'" % op)
#    else:
#        return float(op)
#
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
    def __init__(self, width, height, alg, verbose, fg, bg, filename):
        self.width = width
        self.height = height
        self.alg = alg
        self.verbose = verbose
        self.filename = filename
        if fg is not None:
            self.fghue = colorsys.hsv_to_rgb(fg[0]/255, fg[1]/255, fg[2]/255)
        else:
            self.fghue = colorsys.hsv_to_rgb(0, 0, 1)
        if bg is not None:
            self.bghue = colorsys.hsv_to_rgb(bg[0]/255, bg[1]/255, bg[2]/255)
        else:
            self.bghue = colorsys.hsv_to_rgb(0, 0, 0)
        self.constants = {"ROWS": height, "COLS": width, "MAX": width*height}
        self.optvars = {"X": 0, "Y": 0, "P": 0}
        self.locals = {}
        self.ops = {"+" : np.add,
                    "-" : np.subtract,
                    "*" : np.multiply,
                    "/" : np.divide,
                    "^" : np.power }
        self.fns = {"sin" : np.sin,
                    "cos" : np.cos,
                    "tan" : np.tan,
                    "abs" : np.absolute }

    
    def mainSequence(self):
        self.newImage()
        if self.verbose: vprint("Size:{}\tPixels:{}\tCustom fg/bg color:({}, {})\nRequired variables: {}\nAlgorithm:\n{}\n".format("{}x{}".format(self.width, self.height), self.width*self.height, self.fghue, self.bghue, self.reqvars, self.alg))
        pixeldata = self.crunch()
        self.placePixels(pixeldata)
        self.saveImage()
    
    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':             #negate
            return -self.evaluateStack(s)
        if op in self.ops:                   #perform op
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.ops[op](op1, op2)
        elif op in self.fns:                  #perform fn
            return self.fns[op](evaluateStack(s))
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
        print("\n(This may take a few minutes. Please be patient!)")
        print("Parsing...") #TODO: ADD PROGRESS BAR
        global exprStack #not sure if this is needed
        exprStack = []
        pixeldata = []
        maxp = self.constants["MAX"]
        ws = self.alg.replace("\n", ";").split(";") #lines with leading and/or trailing whitespace
        lines = map(lambda x: x.strip(), ws)
        
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
                    
                        isplit = input_string.split()
                        if isplit[1] != "=":
                            if isplit[0][0] == "$":
                                try:
                                    rand.seed(int(isplit[0][1:]))
                                except:
                                    err("ParseFailure: Line 1\n{}\n ^ invalid seed value".format(input_string))
                            else:
                                missing("=", i, isplit)
                    

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
                                err(str(e))
                            else:
                                self.locals[L.varname] = result
                            #if self.verbose: vprint("variables = {}\n".format(variables))#`
                        else:
                            err("ParseFailure: Line ",   more=True)
                            err(pe.line,                 more=True)
                            err(" "*(pe.column-1) + "^", more=True)
                            err(pe)
                    #end of current line
                for v in self.reqvars:
                    pixval.append(self.locals[v]) #[255,255,255]
                pixeldata.append(pixval)          #[ ..., [255,255,255] ]
                self.optvars["P"] += 1
                #end of column
            #end of row
        return pixeldata
        
    def newImage(self):
        pass
    
    def convert(p): #this will be overridden to return an RGB/CYMK tuple
        pass
    
    def placePixels(self, pixeldata):
        print("Placing pixels...")
        maxp = self.constants["MAX"]
        i = 0
        for y in xrange(self.height):
            for x in xrange(self.width):
                if self.verbose: progbar(i, maxp)
                color = self.convert(pixeldata[i])
                self.pix[x,y] = color
                i += 1
    
    def saveImage(self):
        self.im.save(self.filename, "png")
        print("Saving as {}".format(self.filename))
        
    
    

#http://effbot.org/imagingbook/imagedraw.htm

class ParserGray(Parser):
    def newImage(self):
        self.reqvars = ("K")
        self.im = Image.new("RGB", (self.width, self.height))
        self.pix = self.im.load()

    def convert(self, p):
        r = lerp(self.bghue[0], self.fghue[0], p[0]/255)*255
        g = lerp(self.bghue[1], self.fghue[1], p[0]/255)*255
        b = lerp(self.bghue[2], self.fghue[2], p[0]/255)*255
        return (int(round(r)), int(round(g)), int(round(b)))

#class ParserRGB(Parser):
#    def newImage(self):
#        self.reqvars = ("R", "G", "B")
#        self.im = Image.new("RGB", (self.width, self.height))
#        self.pix = self.im.load()
#    
#    def convert(self, p):
#        return p
#
#class ParserHLS(Parser):
#    def newImage(self):
#        self.reqvars = ("H", "L", "S")
#        self.im = Image.new("RGB", (self.width, self.height))
#        self.pix = self.im.load()
#
#    def convert(self, p):
#        return colorsys.hls_to_rgb(p[0]/255, p[1]/255, p[2]/255)
#    
#class ParserHSV(Parser):
#    def newImage(self):
#        self.reqvars = ("H", "S", "V")
#        self.im = Image.new("RGB", (self.width, self.height))
#        self.pix = self.im.load()
#
#    def convert(self, p):
#        return colorsys.hsv_to_rgb(p[0]/255, p[1]/255, p[2]/255)
#
#class ParserCYMK(Parser):
#    def newImage(self):
#        self.reqvars = ("C", "Y", "M", "K")
#        self.im = Image.new("CYMK", (self.width, self.height))
#        self.pix = self.im.load()
#    
#    def convert(self, p):
#        return p

#class ParserYIQ(Parser):  #TODO
#    def newImage(self):
#        self.reqvars = ("Y", "I", "Q")
#        self.im = Image.new("RGB", (self.width, self.height))
#        self.draw = ImageDraw.Draw(self.im)



#Make a pull request if you want to add more modes!
