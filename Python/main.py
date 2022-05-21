# 2022 Computer Engineering Capstone
# Team: Opto3D / Alcon

# MODE SELECT
#  0 = Original video
#  1 = Left eye monoscopic
#  2 = Right eye monoscopic
#  3 = Top-bottom
#  4 = Row interleaved
# SELECTION (MODE)
MODE = 3

# POLARITY SWAP
#  0 = Default
#  1 = Swapped
# SELECTION (POLARITY)
POLARITY = 0

# IMAGE CORRECTION
#  0 = Default / unaltered output
#  1 = Sepia toning for posterior view
#  2 = Saturation adjustment
SAT_SCALE = 1.5
#  3 = Contrast/brightness adjustment
CONTRAST_SCALE = 1.25
BRIGHT_SCALE = 50
# SELECTION (IMCORR_MODE)
IMCORR_MODE = 0

# INPUT STREAMS (Slight disparity)
VIDEO_LEFT = 'left_camera.mp4'
VIDEO_RIGHT = 'right_camera.mp4'

# DEBUG MESSAGES
VERBOSE = False

# OLD: Previously assumed stereo vision, half resolution, slight disparity
#  This may still be used by feeding side-by-side back to the beginning
VIDEO = 'city_video_1080p.mp4'


from sre_constants import SUCCESS
import cupy as cp # <----------------------------------------	Bug here: cupy or numpy
import sys
sys.path.append('/usr/local/lib/python3.8/site-packages') # Allow Python3.8 to refer to OpenCV4.5.1 install library
import cv2
import argparse


# CHECK AND SET COMMAND LINE ARGUMENTS
parser = argparse.ArgumentParser(description = "Left and Right Camera file names are required, must be in same directory.  Use --help to see optional arguments")

def t_f_checker(a):
    if (a != "True") and (a != "False"):
        raise argparse.ArgumentTypeError(
            'Invalid \'verbose\' argument.  Must be True/False.  Use --help to see options')
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

# Optional arguments
parser.add_argument("-v", "--verbose", help = "Show debugging print statements (True/False)", type = t_f_checker)
parser.add_argument("-m", "--mode", help = "1 = Left Camera\n2 = Right Camera\n3 = Top-Bottom\n4 = Row-Interleaved", type = mode_checker)
parser.add_argument("-p", "--polarity", help = "0 = Default\n1 = Swapped", type = polarity_checker)
parser.add_argument("-c", "--imageCorrection", help = "0 = Unaltered\n1 = Sepia (For posterior view)\n2 = Saturation Adjustment", type = image_corr_checker)
parser.add_argument("-s", "--saturationScale", help = "Default is 1.5", type = float)

# Required arguments
reqNamed = parser.add_argument_group("Required L/R Camera file names")
reqNamed.add_argument("-l", "--leftCamera", help = "Left camera file name", required = True)
reqNamed.add_argument("-r", "--rightCamera", help = "Right camera file name", required = True)

args = parser.parse_args()

# Set video sources:
VIDEO_LEFT = args.leftCamera
VIDEO_RIGHT = args.rightCamera

if args.verbose:
    if args.verbose == "True":
        print("Showing debugging print statements")
        verbose = True
    else:
        print("Debugging print statements disabled")
        verbose = False

if args.mode:
    if (args.mode == 1):
        print("Mode set to Left Camera")
    elif (args.mode == 2):
        print("Mode set to Right Camera")
    elif (args.mode == 3):
        print("Mode set to Top-Bottom")
    elif (args.mode == 4):
        print("Mode set to Row-Interleaved")

    MODE = args.mode

# Argument passed as string, since options are 0 or 1.
if args.polarity:
    if (args.polarity == "0"):
        print("Default polarity")
    elif (args.polarity == "1"):
        print("Swapped polarity")

    POLARITY = int(args.polarity)

# Argument passed as string, since options include 0
if args.imageCorrection:
    if (args.imageCorrection == "0"):
        print("Unaltered image")
    elif (args.imageCorrection == "1"):
        print("Image in Sepia")
    elif(args.imageCorrection == "2"):
        print("Saturation Adjusted")

    IMCORR_MODE = int(args.imageCorrection)

# Argument passed as string, since 0 option is possible
if args.saturationScale:
    print("Saturation scale set to: ", args.saturationScale)

    SAT_SCALE = float(args.saturationScale)



# BEGIN MAIN EXECUTION
# Place odd rows from left above even rows from right
def top_bottom(left_in, right_in, pol):
    if verbose: print('Made it to top-bottom')
    num_rows, num_cols, num_ch = cp.shape(left_in)
    rows = int(num_rows / 2)
    if verbose: print('Before CuPy')
    out = cp.zeros_like(left_in) # <--------------------------	Bug here: cupy version (need 10.2)
    if verbose: print('Splitting...')
    if verbose: print(type(left_in))
    if pol:
        # Polarity is swapped
        out[0:rows,:] = right_in[::2,:]
        out[rows:,:] = left_in[1::2,:]
    else:
        # Default polarity
        out[0:rows,:] = left_in[::2,:]
        out[rows:,:] = right_in[1::2,:]
    if verbose: print('Ready to display')
    display('Top-bottom', out)

# Side-by-side optional

# Interleave odd rows from left and even rows from right
def row_interleaved(left_in, right_in, pol):
    out = cp.zeros_like(left_in)
    if pol:
        # Polarity is swapped
        out[::2,:] = right_in[::2,:]
        out[1::2,:] = left_in[1::2,:]
    else:
        # Default polarity
        out[::2,:] = cp.array(left_in[::2,:])
        out[1::2,:] = cp.array(right_in[1::2,:])
    display('Row interleaved', out)

def original(left_in, right_in, pol):
    out = cp.zeros_like(cp.hstack((left_in, right_in)))
    if pol:
        # Polarity is swapped
        out = cp.hstack((right_in, left_in))
    else:
        # Default polarity
        out = cp.hstack((left_in, right_in))
    display('Original (Side-by-side)', out)

def display(window, output):
    # Fullscreen options for testing
    #cv2.namedWindow(window, cv2.WND_PROP_FULLSCREEN)
    #cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Result 0 -- Unmodified output (Default)
    cp_out = cp.uint8(output.get())         # For CuPy, Comment out for NumPy
    #cp_out = cp.uint8(output)               # For NumPy, Comment out for CuPy
    result = cp_out[:, :, [0, 1, 2]]
    if verbose: print('Attempting to display...')

    # Result 1 -- Sepia toned output
    if IMCORR_MODE==1:
        sepia_kernel = cp.float64([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        cp_out_float = cp.float64(output.get())
        result_2s = cv2.transform(cp_out_float, sepia_kernel)
        #result[cp.where(cp.asarray(result) > 255)] = 255
        result_2c = cp.clip(result_2s, 0, 255)
        result_2a = cp.array(result_2c, dtype=cp.uint8)
        result = cp.uint8(result_2a.get())

    # Result 2 -- Saturation adjustment
    if IMCORR_MODE==2:
        out_hsv = cv2.cvtColor(cp_out, cv2.COLOR_BGR2HSV).astype("float64")
        (h,s,v) = cv2.split(out_hsv)
        s = s*SAT_SCALE
        s = cp.clip(s, 0, 255)
        out_hsv = cv2.merge([h,s,v])
        result = cv2.cvtColor(out_hsv.astype("uint8"), cv2.COLOR_HSV2BGR)

    # Result 3 -- Contrast/brightness increase
    if IMCORR_MODE==3:
        result = cv2.convertScaleAbs(result, alpha=CONTRAST_SCALE, beta=BRIGHT_SCALE)

    if verbose: print('Frame displayed')
    cv2.imshow(window, result)





# Execution continues here
L_capture = cv2.VideoCapture(VIDEO_LEFT)
if verbose: print('Reading first video')
R_capture = cv2.VideoCapture(VIDEO_RIGHT)
if verbose: print('Reading second video')
while(L_capture.isOpened() and R_capture.isOpened()):
    if verbose: print('Capture is open')
    L_success, L_frame = L_capture.read()
    R_success, R_frame = R_capture.read()
    if L_success and R_success:
        if verbose: print('Success')
        num_L_rows, num_L_cols, num_ch = cp.shape(L_frame)
        num_R_rows, num_R_cols, num_ch = cp.shape(R_frame)
        
        # Read into CuPY (Comment out block when using NumPy)
        L_frame = cp.asarray(L_frame)
        R_frame = cp.asarray(R_frame)
        #cols = int(num_cols / 2)
        # Mode select
        if MODE == 1:
            if verbose: print('Left mono/2D')
            display('Left eye monoscopic', L_frame[:,:])
        elif MODE == 2:
            if verbose: print('Right mono/2D')
            display('Right eye monoscopic', R_frame[:,:])
        elif MODE == 3:
            if verbose: print('Top Bottom (3D)')
            top_bottom(L_frame[:,:], R_frame[:,:], POLARITY)
        elif MODE == 4:
            if verbose: print('Interlaced (3D)')
            row_interleaved(L_frame[:,:], R_frame[:,:], POLARITY)
        else:
            # Previously side-by-side (time permitting)
            #original(frame[:,0:cols], frame[:,cols:], POLARITY)
            print(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        L_capture = cv2.VideoCapture(VIDEO_LEFT)
        R_capture = cv2.VideoCapture(VIDEO_RIGHT)


L_capture.release()
R_capture.release()
cv2.destroyAllWindows()
