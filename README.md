# AlgArt
###Algorithmic image generator in python
____

Inspired by the algorithmic music generator, [ByteBeat](http://canonical.org/~kragen/bytebeat/), AlgArt is an image generator that allows you to write your own algorithms to create images.

For example:


```
CODE HERE
```

makes this image:

![test image](LINK)


###Documentation (accessible with -h)
____

```
 
 ./algart -c gray -s <height>x<width> [-f color] [-b color] [-v] (-a algorithm | -i file) -o file
 ./algart -c rgb|hsv|hls|cymk -s <height>x<width> [-v] (-a algorithm | -i file) -o file

 ****
 For in-depth guide and extended usage, run ./algart -h <topic>
 ****
"""

helpstringlong = """Usage:

(lines with ~ are not yet implemented)
 
 ./algart -c gray -s <height>x<width> [-f (h,s,v)] [-b (h,s,v)] [-v] (-a algorithm | -i file) -o file
 ./algart -c rgb|hsv|hls|cymk -s <height>x<width> [-v] (-a algorithm | -i file) -o file
 ./algart -h
 
 Arguments:
 * = required
    -h                                Extended help (you are here)
 *  -c gray|rgb|hsv|hls|cymk|custom   Color mode
 *  -s                                Size of image (height x width)
    -f (h,s,v)                        Foreground color in HSV [0-255] format (grayscale mode only)
    -b (h,s,v)                        Background color in HSV [0-255] format (grayscale mode only)
    -v                                Verbose mode (shows extra info and progress bars, might impact performance)
 *  -a algorithm | -i file            Algorithm to apply or filename of algorithm file
 *  -o file                           Location to save the PNG

 Color modes:
  MODES    REQUIRED VARS    DESCRIPTIONS (assuming max = 255, hue = red)
  gray   - K              - Grayscale (0 = white, 255 = black)
  hsv    - H,S,V          - Hue, Saturation (0 = white, 255 = red), Value (0 = black, 255 = white)
  hls    - H,L,S          - Hue, Luminosity (0 = black, 255 = white), Saturation (0 = gray , 255 = red)
  cymk   - C,Y,M,K        - Cyan, Yellow, Magenta, Key

 Syntax:
    +, -, *, /, %               Arithmetic operators
    ^                           Exponent operator
    (...)                       Parentheses
 ~  {..., ..., ...}[...]        Array definition and index
 ~  <, >, <=, >=, ==, !=        Evaluation (evaluates to 0 [false] or 1 [true])
 ~  ... ? ... : ...             Boolean operators
    =                           Variable assignment
 ~  | ... |                     Absolute value
 ~  (~)&&, (X)(~)||             *Bitwise* expressions
 ~  (N)AND, (X)(N)OR            *Logical* expressions (**CAREFUL!** evaluates to 1 or 0, not bitwise)
    #                           Comment
    $integer                    Set seed for Algart, evaluated as string. Use it as your title! (optional, but recommended)
    
 Built-in functions:
 (read "Defining functions" for why I used 'a' and 'b' for these examples)
 ~  FAC(a)      Factorial "!"
    COS(a)      Cosine
    SIN(a)      Sine
    TAN(a)      Tangent
 ~  RAND(a, b)  Return integer between x and y
 ~  RANDF(a, b) Return float between x and y (discouraged for anything other than RANDF(0, 1))
 ~  FUZZ(a, b)  Return x, increased or decreased up to a maximum of y (this is an easy way to add "fuzz" to your Algart)
    
 Note on entropy:
    Start a file with $ and a number to set the seed for predictable randomness or recreating an example
    For example:
    $5135
    sets an Algart's seed to 5135
 
 Read-only variables:
    X - pixel X coordinate (origin 0,0)
    Y - pixel Y coordinate (origin 0,0)
    P - pixel number (if 256x256 image, 0 - 65536)

 Read-only constants:
    MAX = Total number of pixels
    ROWS = Total rows of pixels (height)
    COLS = Total columns of pixels (width)

 Example usage:
    ./algart.py -c gray -s 256x256 -a "rate = 255 / MAX; k = P * rate" -o test.png
  or using a file instead:   
    ./algart.py -c gray -s 256x256 -i algo.txt -o test.png
    
    algo.txt:
      //This is my file!
      rate = 255 / MAX  //this evaluates to (255/65536 for a 256x256 image)
      K = P * rate
      
    To explain the above usage, since 'P' goes up to 65536 (256x256), "rate" will allow us to scale 'P' down to an 8-bit number.
    This allows us to assign 'K' to a number between 0-255 from a number between 0-65536.
    
 Style guide:
    - User-defined variables should be lowercase. (halfrate = myvar * 0.5)
    - Read-only variables/required variables/pre-defined functions should be uppercase. (COLS, K, SIN(), etc.)
    - Spaces = readability. (You'll notice this if you read my source! Also, please don't, because it's sloppy.).
    - End Algart files with .alg, even though it isn't required. (It'll be a thing, I swear!)
    
```