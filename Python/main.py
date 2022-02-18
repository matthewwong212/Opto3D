# 2022 ECE 189 Capstone
# Opto3D / Alcon
#
# Source Video - Credit:
#  "San Francisco in Stereo 3D - SBS" by Azad Balabanian, YouTube.com
#  https://www.youtube.com/watch?v=fs_Uw4qL2O8

from sre_constants import SUCCESS
import jetson.utils
import numpy as np
import cv2

# MODE SELECT
#  0 = Original video
#  1 = Left eye monoscopic
#  2 = Right eye monoscopic
#  3 = Top-bottom
#  4 = Row interleaved
MODE = 4
# POLARITY SWAP
#  0 = Default
#  1 = Swapped
POLARITY = 0
# VIDEO NAME
#  Assumes stereo vision, half resolution, slight disparity
VIDEO = 'city_video_1080p.mp4'



# Place odd rows from left above even rows from right
def top_bottom(left_in, right_in, pol):
    num_rows, num_cols, num_ch = np.shape(left_in)
    rows = int(num_rows / 2)
    out = np.zeros_like(left_in)
    if pol:
        # Polarity is swapped
        out[0:rows,:] = right_in[::2,:]
        out[rows:,:] = left_in[1::2,:]
    else:
        # Default polarity
        out[0:rows,:] = left_in[::2,:]
        out[rows:,:] = right_in[1::2,:]
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
        out[::2,:] = left_in[::2,:]
        out[1::2,:] = right_in[1::2,:]
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

def display(window, output):
#   cv2.namedWindow(window, cv2.WND_PROP_FULLSCREEN)
#   cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window, output)



# Execution continues here
capture = cv2.VideoCapture(VIDEO)
while(capture.isOpened()):
    success, frame = capture.read()
    frame=cudaFromNumpy(frame)
    if success:
        num_rows, num_cols, num_ch = np.shape(frame)
        cols = int(num_cols / 2)
        # Mode select
        if MODE == 1:
            display('Left eye monoscopic', frame[:,0:cols])
        elif MODE == 2:
            display('Right eye monoscopic', frame[:,cols:])
        elif MODE == 3:
            top_bottom(frame[:,0:cols], frame[:,cols:], POLARITY)
        elif MODE == 4:
            row_interleaved(frame[:,0:cols], frame[:,cols:], POLARITY)
        else:
            original(frame[:,0:cols], frame[:,cols:], POLARITY)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        capture = cv2.VideoCapture(VIDEO)

capture.release()
cv2.destroyAllWindows()
