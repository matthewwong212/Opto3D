import argparse

def t_f_checker(a):
    if (a != "True") and (a != "False"):
        raise argparse.ArgumentTypeError(
            'Invalid argument.  Must be True/False.  Use --help to see options')
    return a

def mode_checker(a):
    try:
        asInt = int(a)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Invalid \'mode\' argument. Must be an integer between 1 and 4.  Use --help to see options.')

    if asInt > 4 or asInt < 1:
        raise argparse.ArgumentTypeError(
            'Invalid \'mode\' argument. Must be an integer between 1 and 4.  Use --help to see options.')
    return asInt

def polarity_checker(a):
    try:
        asInt = int(a)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Invalid \'polarity\' argument. 0 = Default, 1 = Swapped.  Use --help to see options.')

    if asInt > 1 or asInt < 0:
        raise argparse.ArgumentTypeError(
            'Invalid \'polarity\' argument. 0 = Default, 1 = Swapped.  Use --help to see options.')
    return a

def image_corr_checker(a):
    try:
        asInt = int(a)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Invalid \'image-correction\' argument.  0 = Unaltered\n1 = Sepia (For posterior view)\n2 = Saturation Adjustment  Use --help to see options.')

    if asInt > 2 or asInt < 0:
        raise argparse.ArgumentTypeError(
            'Invalid \'image-correction\' argument.  0 = Unaltered\n1 = Sepia (For posterior view)\n2 = Saturation Adjustment  Use --help to see options.')
    return a

def sat_checker(a):
    try:
        asFloat = float(a)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Invalid \'saturationScale\' argument. Must be a float from x -> y.  Use --help to see options.')

    return a

def create_parser():

    parser = argparse.ArgumentParser(description = "Left and Right Camera file names are required, must be in same directory.  Use --help to see optional arguments")

    # Optional arguments
    parser.add_argument("-v", "--verbose", help = "Show debugging print statements (True/False)", type = t_f_checker)
    parser.add_argument("-m", "--mode", help = "1 = Left Camera\n2 = Right Camera\n3 = Top-Bottom\n4 = Row-Interleaved", type = mode_checker)
    parser.add_argument("-p", "--polarity", help = "0 = Default\n1 = Swapped", type = polarity_checker)
    parser.add_argument("-i", "--imageCorrection", help = "0 = Unaltered\n1 = Sepia (For posterior view)\n2 = Saturation Adjustment", type = image_corr_checker)
    parser.add_argument("-s", "--saturationScale", help = "Default is 1.5", type = float)
    parser.add_argument("-f", "--fullscreen", help = "Show in fullscreen (True/False)", type = t_f_checker)
    parser.add_argument("-o", "--outFilename", help = "Specifies filename when writing video to file")
    parser.add_argument("-a", "--saveVideo", help = "Save to a .avi file (True/False).  Saves entire video when looping", type = t_f_checker)
    parser.add_argument("-t", "--loop", help = "Loop input videos (True/False)", type = t_f_checker)


    # Required arguments
    reqNamed = parser.add_argument_group("Required L/R Camera file names")
    reqNamed.add_argument("-l", "--leftCamera", help = "Left camera file name", required = True)
    reqNamed.add_argument("-r", "--rightCamera", help = "Right camera file name", required = True)

    return parser
