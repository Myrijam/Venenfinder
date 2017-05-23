#!/usr/bin/python
# -*- coding: utf-8 -*-
# import the necessary packages / mobile Venenfinder
#
# We used some code as inspiration and as a starting point
# Streaming Server for MJPG from Igor Maculan 
# https://gist.github.com/n3wtron/4624820
# we changed it to Pycam, added encoders and display of parameters...
# Encoder examples and library:
# http://www.bobrathbone.com/raspberrypi/Raspberry%20Rotary%20Encoders.pdf

from __future__ import print_function

#from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
#import argparse
#import imutils
import time
import cv2
import numpy as np
from threading import Thread

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn

from rotary_class_2 import RotaryEncoder

count3 = 180
PIN_A3 = 23
PIN_B3 = 18

count1 = 40
PIN_A1 = 20
PIN_B1 = 21

count2 = 80
PIN_A2 = 24
PIN_B2 = 25

einstellung = False

#xres = 690
#yres = 300

# Größe der angezeigten Bilder
img_res_x = 800
img_res_y = 608


#x_roi = (img_res_x-xres)/2
#y_roi = (img_res_y-yres)/2


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global count1
        global count2
        global count3
        global x_roi
        global y_roi
        global xres
        global yres
        global camera
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            while True:
                   #Kamerabilder einlesen
                    img = vs.read()
                    #img = cv2.flip(img,1)
                    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    # Anpassung der Grauverteilung (adaptives Verfahren)
                    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))
                    cl1 = clahe.apply(img_grey)

                    #cl1 = cv2.equalizeHist(img_grey)
                    clamp = np.uint8(np.interp(cl1, [count2, count3],[0,255]))

                    # neue adaptive Anpassung mit den Grenzwerten -> speichern in neuem Bild
                    equ = clahe.apply(clamp)
                    #equ = cv2.equalizeHist(clamp)
                    r,buf = cv2.imencode('.jpg', equ)

                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(len(buf)))
                    self.end_headers()
                    self.wfile.write(bytearray(buf))
                    #print (count2)
                    time.sleep(0.05)



        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="http://127.0.0.1:8080/cam.mjpg"/>')
            self.wfile.write('</body></html>')
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ nothing to see here """


class PiVideoStream:
    global count1
    #
    def __init__(self, resolution=(320, 240), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        #if (einstellung != True):
        einstellung = True
        
        #print (count1)
        self.camera.iso = 400
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
                # grab the frame from the stream and clear the stream in
                # preparation for the next frame
                self.frame = f.array
                self.rawCapture.truncate(0)

                # if the thread indicator variable is set, stop the thread
                # and resource camera resources
                if self.stopped:
                        self.stream.close()
                        self.rawCapture.close()
                        self.camera.close()
                        return
    def read(self):
            # return the frame most recently read
            self.camera.brightness = count1
            self.camera.annotate_text_size = 20
            #self.camera.annotate_foreground = Color(0,0,1)
            self.camera.annotate_background = True
            self.camera.annotate_text = "H: "+ str(count1)+ "  S: "+ str(count2)+ "  W: "+ str(count3)
            #print(count1)
            return self.frame

    def stop(self):
            # indicate that the thread should be stopped
            self.stopped = True





##



def switch_event1(event):
        global count1
        if event == RotaryEncoder.CLOCKWISE:
                #print "Clockwise"
                count1 = count1+5
                if count1 > 90:
                        count1 = 90
                #print count1        
        elif event == RotaryEncoder.ANTICLOCKWISE:
                #print "Anticlockwise"
                count1 = count1-5
                if count1 < 10:
                        count1 = 10
                #print count1
        return

def switch_event2(event):
        global count2
        if event == RotaryEncoder.CLOCKWISE:
                #print "Clockwise"
                count2 = count2+5
                if count2 > 180:
                        count2 = 180
                #print count2        
        elif event == RotaryEncoder.ANTICLOCKWISE:
                #print "Anticlockwise"
                count2 = count2-5
                if count2 < 80:
                        count2 = 80
                #print count2
        return

def switch_event3(event):
        global count3
        if event == RotaryEncoder.CLOCKWISE:
                #print "Clockwise"
                count3 = count3+5
                if count3 > 220:
                        count3 = 220
                #print count3        
        elif event == RotaryEncoder.ANTICLOCKWISE:
                #print "Anticlockwise"
                count3 = count3-5
                if count3 < 150:
                        count3 = 150
                #print count3
        return



# Define the switch

hell = RotaryEncoder(PIN_A1,PIN_B1,switch_event1)
lower = RotaryEncoder(PIN_A2,PIN_B2,switch_event2)
higher = RotaryEncoder(PIN_A3,PIN_B3,switch_event3)
		

#
# initialize the camera and stream
camera = PiCamera()

camera.resolution = (img_res_x, img_res_y)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(img_res_x, img_res_y))

stream = camera.capture_continuous(rawCapture, format="bgr",
	use_video_port=True)

# allow the camera to warmup and start the FPS counter
print("[INFO] sampling frames from `picamera` module...")
time.sleep(.1)

stream.close()
rawCapture.close()
camera.close()


# created a *threaded *video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from `picamera` module...")
vs = PiVideoStream((img_res_x, img_res_y), 20).start()


time.sleep(1.0)

#while True:
#        frame = vs.read()
#        cv2.imshow("Frame", frame)
#        key = cv2.waitKey(1) & 0xFF

#### server start



server = ThreadedHTTPServer(('192.168.42.1',8080),CamHandler)
server.serve_forever()
server.socket.close()



