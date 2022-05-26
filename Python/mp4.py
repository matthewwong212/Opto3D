# 2022 Computer Engineering Capstone
# Team: Opto3D / Alcon

# MODE SELECT
#  0 = Original video
#  1 = Left eye monoscopic
#  2 = Right eye monoscopic
#  3 = Top-bottom
#  4 = Row interleaved
MODE = 3

# POLARITY SWAP
#  0 = Default
#  1 = Swapped
#  SELECTION (POLARITY)
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
VIDEO_LEFT = 'left_v2_1080.mp4'
VIDEO_RIGHT = 'right_v2_1080.mp4'

# DEBUG MESSAGES
VERBOSE = False

# Set CuPy or NumPy Execution. Internal testing only.
USE_CUPY = False

# Set Fullscreen option
FULL = False

# To tune delay between frames depending on CPU
FRAMEDELAY = 7

# OLD: Previously assumed stereo vision, half resolution, slight disparity
#  This may still be used by feeding side-by-side back to the beginning
# VIDEO = 'city_video_1080p.mp4'


from sre_constants import SUCCESS
import sys
#sys.path.append('/usr/local/lib/python3.8/site-packages') # Allow Python3.8 to refer to OpenCV4.5.1 install library
import cv2
import argparse_file
if USE_CUPY:
    import cupy as np
else:
    import numpy as np

def set_args():
    global MODE, VERBOSE, VIDEO_LEFT, VIDEO_RIGHT, IMCORR_MODE, POLARITY, SAT_SCALE, FULL
    # Gets parsed command line arguments from argparse_file
    parser = argparse_file.create_parser()
    args = parser.parse_args()

    # Set video sources:
    VIDEO_LEFT = args.leftCamera
    VIDEO_RIGHT = args.rightCamera

    # Set debugging messages
    if args.verbose:
        if args.verbose == "True":
            print("Showing debugging print statements")
            VERBOSE = True
        else:
            print("Debugging print statements disabled")
            VERBOSE = False

    if args.fullscreen:
        if args.fullscreen == "True":
            print("Fullscreen Mode")
            FULL = True
        else:
            print("Windowed Mode")
            FULL = False

    # Set chosen mode
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


    # Set polarity.  Argument passed as string, since options are 0 or 1.
    if args.polarity:
        if (args.polarity == "0"):
            print("Default polarity")
        elif (args.polarity == "1"):
            print("Swapped polarity")

        POLARITY = int(args.polarity)

    # Set image correction mode.  Argument passed as string, since options include 0
    if args.imageCorrection:
        if (args.imageCorrection == "0"):
            print("Unaltered image")
        elif (args.imageCorrection == "1"):
            print("Image in Sepia")
        elif(args.imageCorrection == "2"):
            print("Saturation Adjusted")

        IMCORR_MODE = int(args.imageCorrection)

    # Set saturation scale.  Argument passed as string, since 0 option is possible
    if args.saturationScale:
        print("Saturation scale set to: ", args.saturationScale)

        SAT_SCALE = float(args.saturationScale)


# BEGIN MAIN EXECUTION
# Place odd rows from left above even rows from right
def top_bottom(left_in, right_in, pol):
    if VERBOSE: print('Made it to top-bottom')
    num_rows, num_cols, num_ch = np.shape(left_in)
    rows = int(num_rows / 2)
    if VERBOSE: print('Before CuPy')
    out = np.zeros_like(left_in)
    if VERBOSE: print('Splitting...')
    if pol:
        # Polarity is swapped
        out[0:rows,:] = right_in[::2,:]
        out[rows:,:] = left_in[1::2,:]
    else:
        # Default polarity
        out[0:rows,:] = left_in[::2,:]
        out[rows:,:] = right_in[1::2,:]
    if VERBOSE: print('Ready to display')
    display('Top-bottom', out)

# Interleave odd rows from left and even rows from right
def row_interleaved(left_in, right_in, pol):
    out = np.zeros_like(left_in)
    if pol:
        # Polarity is swapped
        out[::2,:] = right_in[::2,:]
        out[1::2,:] = left_in[1::2,:]
    else:
        # Default polarity
        out[::2,:] = np.array(left_in[::2,:])
        out[1::2,:] = np.array(right_in[1::2,:])
    display('Row interleaved', out)

def original(left_in, right_in, pol):
    out = np.zeros_like(np.hstack((left_in, right_in)))
    if pol:
        # Polarity is swapped
        out = np.hstack((right_in, left_in))
    else:
        # Default polarity
        out = np.hstack((left_in, right_in))
    display('Original (Side-by-side)', out)

# Main display execution
def display(window, output):
    global MODE, VERBOSE, VIDEO_LEFT, VIDEO_RIGHT, IMCORR_MODE, POLARITY, SAT_SCALE, FULL
    # Fullscreen options for testing
    if FULL:
        cv2.namedWindow(window, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Result 0 -- Unmodified output (Default)
    # Differing lines for CuPy vs NumPy
    if USE_CUPY:
        np_out = np.uint8(output.get())
    else:
        np_out = np.uint8(output)

    result = np_out[:, :, [0, 1, 2]]
    if VERBOSE: print('Attempting to display...')

    # Result 1 -- Sepia toned output
    if IMCORR_MODE==1:
        sepia_kernel = np.float64([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        if USE_CUPY:
            np_out_float = np.float(output.get())
        else:
            np_out_float = np.float64(output)
        result_2s = cv2.transform(np_out_float, sepia_kernel)
        #result[np.where(np.asarray(result) > 255)] = 255
        result_2c = np.clip(result_2s, 0, 255)
        result_2a = np.array(result_2c, dtype=np.uint8)
        # result = np.uint8(result_2a.get())
        if USE_CUPY:
            result = np.uint8(result_2a.get())
        else:
            result = np.uint8(result_2a)

    # Result 2 -- Saturation adjustment
    if IMCORR_MODE==2:
        out_hsv = cv2.cvtColor(np_out, cv2.COLOR_BGR2HSV).astype("float64")
        (h,s,v) = cv2.split(out_hsv)
        s = s*SAT_SCALE
        s = np.clip(s, 0, 255)
        out_hsv = cv2.merge([h,s,v])
        result = cv2.cvtColor(out_hsv.astype("uint8"), cv2.COLOR_HSV2BGR)

    # Result 3 -- Contrast/brightness increase
    if IMCORR_MODE==3:
        result = cv2.convertScaleAbs(result, alpha=CONTRAST_SCALE, beta=BRIGHT_SCALE)

    if VERBOSE: print('Frame displayed')
    cv2.imshow(window, result)


def main():
    global MODE, VERBOSE, VIDEO_LEFT, VIDEO_RIGHT, IMCORR_MODE, POLARITY, SAT_SCALE, FULL, FRAMEDELAY
    global FRAMES = []
    # Execution continues here
    L_capture = cv2.VideoCapture(VIDEO_LEFT)
    if VERBOSE: print('Reading first video')
    R_capture = cv2.VideoCapture(VIDEO_RIGHT)
    if VERBOSE: print('Reading second video')
    while(L_capture.isOpened() and R_capture.isOpened()):
        if VERBOSE: print('Capture is open')
        L_success, L_frame = L_capture.read()
        R_success, R_frame = R_capture.read()
        if L_success and R_success:
            if VERBOSE: print('Success')
            num_L_rows, num_L_cols, num_ch = np.shape(L_frame)
            num_R_rows, num_R_cols, num_ch = np.shape(R_frame)
            
            # Read into CuPY (Comment out block when using NumPy)
            L_frame = np.asarray(L_frame)
            R_frame = np.asarray(R_frame)
            #cols = int(num_cols / 2)
            # Mode select
            if MODE == 1:
                if VERBOSE: print('Left mono/2D')
                display('Left eye monoscopic', L_frame[:,:])
            elif MODE == 2:
                if VERBOSE: print('Right mono/2D')
                display('Right eye monoscopic', R_frame[:,:])
            elif MODE == 3:
                if VERBOSE: print('Top Bottom (3D)')
                top_bottom(L_frame[:,:], R_frame[:,:], POLARITY)
            elif MODE == 4:
                if VERBOSE: print('Interlaced (3D)')
                row_interleaved(L_frame[:,:], R_frame[:,:], POLARITY)
            else:
                # Previously side-by-side (time permitting)
                #original(frame[:,0:cols], frame[:,cols:], POLARITY)
                print(1)
        else:
            L_capture = cv2.VideoCapture(VIDEO_LEFT)
            R_capture = cv2.VideoCapture(VIDEO_RIGHT)

        key = cv2.waitKey(FRAMEDELAY)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('m'):
            cv2.destroyAllWindows()
            if MODE == 4:
                MODE = 1
            else:
                MODE += 1
        elif key & 0xFF == ord('p'):
            cv2.destroyAllWindows()
            if POLARITY == 0:
                POLARITY = 1
            else:
                POLARITY = 0
        elif key & 0xFF == ord('i'):
            cv2.destroyAllWindows()
            if IMCORR_MODE == 0:
                IMCORR_MODE = 1
            else:
                IMCORR_MODE = 0


    L_capture.release()
    R_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    set_args()
    main()
