# General setup & usage

## Prerequisites:
Python 3.7+

Numpy 1.22.3+

Cupy 10.4+ (Cupy version is specific to corresponding CUDA version)

For functionality on the Xavier NX, run program with ```python3.8``` in place of ```python```, and uncomment line 59: ```sys.path.append('/usr/local/lib/python3.8/site-packages')```

For GPIO functionality on the Xavier NX, install [Jetson GPIO](https://github.com/NVIDIA/jetson-gpio).  Run ```main_GPIO.py``` instead.

## Usage:

**Options to set in main.py file**

**USE_CUPY:** boolean enables/disables Cupy array usage.  Not currently useful, as we suspect the latency and low framerate is bottlenecked by OpenCV reading in frames to CPU memory, and needing a copy to GPU memory.

**FRAMEDELAY:** Int value sets ```cv2.waitKey()``` value.  Should be set to ```1``` when running on Jetson devices.  May need to be set higher on more powerful devices to match processing power to input file framerate.




**Required arguments:**

| Argument | Description |
| ----------- | ----------- |
| -l --leftCamera | Left camera input file |
| -r --rightCamera | Right camera input file | 

**Optional arguments:**

| Argument | Description |
| ---------- | ---------- |
| -h --help | Shows all command line arguments |
| -m --mode | 3D mode to start on.  Defaults to Top/Bottom. 1 = Left, 2 = Right, 3 = Top/Bottom, 4 = Row Interleaved |
| -f --fullscreen | Fullscreen mode. Defaults to windowed. (True/False) |
| -t --loop | Loop input videos. Defaults to True.  (True/False) |
| -p --polarity | Set polarity. 0 = Default, 1 = Swapped |
| -i --imageCorrection | Set image correction type.  Defaults to none. 0 = None, 1 = Sepia, 2 = Saturation Adjustment |
| -s --saturationScale | Set saturation value.  Must also enable image correction |
| -a --saveVideo | Enable/disable writing output video to .avi file. Disabled by default (True/False) |
| -o --outFilename | Specify output filename.  No file extension. |
| -v --verbose | Enable/disable debugging and status messages.  WARNING: PRINT STATEMENTS CAUSE SIGNIFICANT PERFORMANCE HIT |
