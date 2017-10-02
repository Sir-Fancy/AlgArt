#!/usr/bin/env python
#
#  Algorithmic art generator
#  Create patterns from user-defined algorithms
# 
#
# Zack Marotta  (c)

import PIL
import numpy
import sys
import os.path
from libalgart.parser import *
from libalgart.user import *


helpstring = """Usage:
 
 ./algart.py -c gray -s <height>x<width> [-f color] [-b color] [-v] [-D] (-a algorithm | -i file) -o file
 ./algart.py -c rgb|hsv|hls|cymk -s <height>x<width> [-v] [-D] (-a algorithm | -i file) -o file

 ****
 For in-depth guide and extended usage, run ./algart -h
 ****
"""

helpstringlong = """(lines with ~ are not yet implemented)
 
 ./algart -c gray -s <height>x<width> [-f "H,L,S"] [-b "H,L,S"] [-v] (-a algorithm | -i file) -o file
 ./algart -c rgb|hsv|hls|cymk -s <height>x<width> [-v] (-a algorithm | -i file) -o file
 ./algart -h
 
 Arguments:
 * = required
    -h                                Extended help (you are here)
 *  (-c | -C) gray|rgb|hsv|hls|cymk   Color mode (READ BELOW!!)
 *  -s <height>x<width>               Size of image
    -f (h,s,v)                        Foreground color in HLS "0-360,0-1,0-1" format (grayscale mode only)
    -b (h,s,v)                        Background color in HLS "0-360,0-1,0-1" (grayscale mode only)
    -v                                Verbose mode (shows extra info and progress bars, might impact performance)
    -D                                Debug; outputs individual pixel values to debug.txt (overwrites previous)
 *  -a algorithm | -i file            Algorithm to apply or filename of algorithm file
 *  -o file                           Location to save the PNG

 Important -c vs -C usage:
    -c specifies a colormode in *clamp mode*
    -C specifies a colormode in *creative mode*
    Clamp mode expects color values for required values to be 0-255. If it is out of range, then it will be clamped within the bounds.
    Creative mode will find the highest number used, and use that as the new max value. (Minimum will still be clamped to 0)
      For example, in creative mode, if you had four values for pixels, (1, 500, 250, 1000), these numbers will become (0.255, 127, 63.5, 255).


 Color modes:
  MODES    REQUIRED VARS    DESCRIPTIONS (assuming max = 255, hue = red)
  gray   - K              - Grayscale       (0 = black, 255 = white)
  hsv    - H,S,V          - Hue, Saturation (0 = white, 255 = red), Value (0 = black, 255 = white)
  hls    - H,L,S          - Hue, Luminosity (0 = black, 255 = white), Saturation (0 = gray , 255 = red)
  cymk   - C,Y,M,K        - Cyan, Yellow, Magenta, Key

 Syntax:
    +, -, *, /, %               Arithmetic operators
    ^                           Exponent operator
    (...)                       Parentheses
    <, >, <=, >=, ==, !=        Evaluation (evaluates to 0 [false] or 1 [true])
    =                           Variable assignment
    (~)&&, (X)(~)||, <<, >>     *Bitwise* operators
    (N)AND, (X)(N)OR            *Logical* operators (**CAREFUL!** evaluates to 1 or 0, not bitwise)
    #                           Comment
    $string                     Set seed for Algart, evaluated as string. Use it as your title! (optional, but recommended)
    
 Built-in functions:
    FAC(a)      Factorial "!"
    SIN(a)      Sine (all trig functions use radians)
    COS(a)      Cosine
    TAN(a)      Tangent
    SINH(a)     Sine, hyperbolic
    COSH(a)     Cosine, hyperbolic
    TANH(a)     Tangent, hyperbolic
    ABS(a)      Absolute value
    SQRT(a)     Square root
    RAND(0)     Random float (0, 1]  **Must have argument, even though it's unused**
     
 Note on entropy:
    Start a file with $ and a number to set the seed for predictable randomness or recreating an example
    For example:
    $foo
    sets an Algart's RNG seed to "foo"
    NOTE: THIS DOESN'T DO ANYTHING YET
 
 Read-only variables:
    X - pixel X coordinate (origin 0,0)
    Y - pixel Y coordinate (origin 0,0)
    P - pixel number (if 256x256 image, 0 - 65536)

 Read-only constants:
    MAX = Total number of pixels
    ROWS = Total rows of pixels (height)
    COLS = Total columns of pixels (width)

 Example usage:
    ./algart -c gray -s 256x256 -a "rate = 255 / MAX; k = P * rate" -o test.png
  or using a file instead:   
    ./algart -c gray -s 256x256 -i algo.txt -o test.png
    
    algo.txt:
      #This is my file!
      rate = 255 / MAX  #this evaluates to (255/65536 for a 256x256 image)
      K = P * rate
      
    To explain the above usage, since 'P' goes up to 65536 (256x256), "rate" will allow us to scale 'P' down to an 8-bit number.
    This allows us to assign 'K' to a number between 0-255 from a number between 0-65536.
    This creates a gradient from top to bottom. Technically, it (essentially) makes this:
    01 02 03 04 05
    06 07 08 09 10
    11 12 13 14 15
    16 17 18 19 20
    But it looks close enough. And yes, "K = Y" would be better, but that's too easy.
    
 Style guide:
    - User-defined variables should be lowercase. (halfrate = myvar * 0.5)
    - Read-only variables/required variables/pre-defined functions should be uppercase. (COLS, K, SIN(), etc.)
    - Spaces = readability. (You'll notice this if you read my source! Also, please don't, because it's sloppy.).
    - End Algart files with .alg, even though it isn't required. (It'll be a thing, I swear!)  
"""
#
#    $string                     Set seed for Algart, evaluated as string. Use it as your title! (optional, but recommended)
#
# Note on entropy:
#    Start a file with $ and a number to set the seed for predictable randomness or recreating an example
#    For example:
#    $foo
#    sets an Algart's RNG seed to "foo"
#    NOTE: THIS DOESN'T DO ANYTHING YET
 


def main():
    # ./algart.py -c gray -s <height>x<width> -d <color-depth> [-f color] [-b color] [-a <algorithm>]
    #global helpstring, helpstringlong
    args = sys.argv
    isclamp = None
    if "-h" in args:
        print(helpstringlong)
        sys.exit(0)
    if len(args) == 1:
        print(helpstring)
        #sys.exit(0)
    
    if "-v" in args:
        verbose = True
    else:
        verbose = False
    
    if "-D" in args:
        debug = True
    else:
        debug = False
    
    if "-s" in args:
        dimensions = args[args.index("-s")+1]
        try:
            width, height = map(int, dimensions.split("x"))
        except ValueError:
            err("ValueError: Invalid -s value, should be format \"WIDTHxHEIGHT\"")
    else:
        err("MissingArgument: \"-s <height>x<width>\"  Size of image (height x width)")
    
    modes = {"gray": ParserGray, "rgb": ParserRGB, "hsv": ParserHSV, "hls": ParserHLS, "cymk": ParserCYMK} 
    if "-c" in args:
        colormode = args[args.index("-c")+1]
        isclamp = True 
        if colormode not in modes:
            err("ValueError: Invalid color mode (-c gray|rgb|hsv|hsl|cymk)")
    if "-C" in args:
        if isclamp: err("ConflictingArguments: Choose either -c OR -C")
        colormode = args[args.index("-C")+1]
        isclamp = False
        if colormode not in modes:
            err("ValueError: Invalid color mode (-C gray|rgb|hsv|hsl|cymk)")
    if isclamp is None: err("MissingArgument: Color mode ([-c|-C] gray|rgb|hsv|hsl|cymk)")
    
    if "-i" in args:
        algfile = args[args.index("-i")+1]
        if os.path.isfile(algfile):
            fopen = open(algfile, "r")
            alg = fopen.read()
        else:
            err("File \"{}\" not found".format(algfile))
    elif "-a" in args:
        alg = args[args.index("-a")+1]
    else:
        err("MissingArgument: \"-a algorithm\", or \"-i file\"")
    
    fgcolorval = None
    bgcolorval = None
    
    if "-f" in args:
        if colormode == "gray":
            fgstr = args[args.index("-f")+1].split(",")
            fgcolorval = map(float, fgstr)
            if fgcolorval[0] > 360 or fgcolorval[0] < 0:
                err("ValueError: Foreground color out of range. Must be format (0-360, 0.0-1.0, 0.0-1.0)")
            for fg in fgcolorval[1:]:
                if fg < 0.0 or fg > 1.0:
                    err("ValueError: Foreground color out of range. Must be format (0-360, 0.0-1.0, 0.0-1.0)")
        else:
            err("InvalidArgument: -f not applicable for colormode \"{}\"".format(colormode))
    if "-b" in args:
        if colormode == "gray":
            bgstr = args[args.index("-b")+1].split(",")
            bgcolorval = map(float, bgcolorval)
            if bgcolorval[0] > 360 or bgcolorval[0] < 0:
                err("ValueError: Background color out of range. Must be format (0-360, 0.0-1.0, 0.0-1.0)")
            for bg in bgcolorval[1:]:
                if bg < 0.0 or bg > 1.0:
                    err("ValueError: Background color out of range. Must be format (0-360, 0.0-1.0, 0.0-1.0)")
        else:
            err("InvalidArgument: -b not applicable for colormode \"{}\"".format(colormode))

    if "-o" in args:
        filename = args[args.index("-o")+1]
    else:
        err("MissingArgument: -o output filename")    
    
    parse = modes[colormode](isclamp, width, height, alg, verbose, debug, fgcolorval, bgcolorval, filename)
    parse.mainSequence()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        err("\nAborted")