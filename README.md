# AlgArt
###Algorithmic image generator in python
____

Inspired by the algorithmic music generator, [ByteBeat](http://canonical.org/~kragen/bytebeat/), AlgArt is an image generator that allows you to write your own algorithms to create images.

For example:


```
/algart -c gray -s 64x64 -v -a "K = SIN(P) * 255" -o lel.png
```

makes this image:

![test image](http://i.imgur.com/NLb1Mie.png)


###Documentation (accessible with -h)
____

```
(lines with ~ are not yet implemented)
 
 ./algart -c gray -s <height>x<width> [-f (h,s,v)] [-b (h,s,v)] [-v] (-a algorithm | -i file) -o file
 ./algart -c rgb|hsv|hls|cymk -s <height>x<width> [-v] (-a algorithm | -i file) -o file
 ./algart -h
 
 Arguments:
 * = required
    -h                                Extended help (you are here)
 *  (-c | -C) gray|rgb|hsv|hls|cymk   Color mode (READ BELOW!!)
 *  -s <height>x<width>               Size of image
    -f (h,s,v)                        Foreground color in HSV [0-255] format (grayscale mode only)
    -b (h,s,v)                        Background color in HSV [0-255] format (grayscale mode only)
    -v                                Verbose mode (shows extra info and progress bars, might impact performance)
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
    SIN(a)      Sine
    COS(a)      Cosine
    TAN(a)      Tangent
    SINH(a)     Sine, hyperbolic
    COSH(a)     Cosine, hyperbolic
    TANH(a)     Tangent, hyperbolic
    ABS(a)      Absolute value
    
 Note on entropy:
    Start a file with $ and a number to set the seed for predictable randomness or recreating an example
    For example:
    $foo
    sets an Algart's RNG seed to "foo"
 
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
      //This is my file!
      rate = 255 / MAX  //this evaluates to (255/65536 for a 256x256 image)
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
```

###Pro tips
____

* Use a small image size like 64x64 and plug it into your favorite image editor to scale it up. Make sure "Nearest Neighbor" interpolation is selected, if available. This will perserve each pixel's sharp edges.
* 