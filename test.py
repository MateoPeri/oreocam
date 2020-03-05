# import the necessary packages
from imutils.video import VideoStream
import cv2, imutils
import time

# initialize the video stream and allow the camera sensor to warmup
cam = cv2.VideoCapture(0)
while True:
    ret_val, img = cam.read()
    cv2.imshow('my webcam', img)
    if cv2.waitKey(1) == 27: 
        break  # esc to quit

cv2.destroyAllWindows()