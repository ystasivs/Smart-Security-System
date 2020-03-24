import cv2
import numpy as np
import time
import math

class Box():
    def __init__(self, box, ID=0):
        self.x1, self.y1, self.x2, self.y2 = box
        self.id = ID
        self.label = 'undefined'
        self.updateStatus = False
        self.sess_start_time = time.time()
    
    def drawBox(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX 
        org = (self.x1, self.y1-3) 
        fontScale = 0.5
        color = (0, 0, 255) 
        thickness = 1
        frame = cv2.putText(frame, f"{self.label} ID:{self.id}", org, font, fontScale,  
                 color, thickness, cv2.LINE_AA, False) 
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), color, int(round(frame.shape[0]/150)), 8)
    
    def updateCoords(self, next_box):
        self.x1, self.y1, self.x2, self.y2 = next_box
    
    #FIXME write isNextFrame
    def isNextFrame(self, box):
        if self.updateStatus == False:
            thresh = math.sqrt((self.x1 - self.x2)**2 + (self.y1 - self.y2)**2) / 2
            if math.sqrt((self.x1 - box[0])**2 + (self.y1 - box[1])**2) < thresh:
                return True
        return False

    def crop_image(self, frame):
        return frame[self.y1 : self.y2, self.x1 : self.x2] 
    
    def __str__(self):
        return f"{self.label}, {self.id}"