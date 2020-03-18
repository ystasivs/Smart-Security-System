import cv2
import threading
import argparse
import numpy as np
import os
import queue
import time

exitFlag = 0
DNN = 'TF'

class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print("Starting server comunication thread")
        print("Exiting server communication thread")

class Box():
    def __init__(self, x1, y1, x2, y2, ID=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.id = ID
        self.label = 'undefined'
        #self.sess_start_time = time.time()
    
    def drawBox(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX 
        org = (self.x1, self.y1-3) 
        fontScale = 0.5
        color = (0, 0, 255) 
        thickness = 1
        frame = cv2.putText(frame, self.label, org, font, fontScale,  
                 color, thickness, cv2.LINE_AA, False) 
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), int(round(frame.shape[0]/150)), 8)
    
    def crop_image(self, frame):
        return frame[self.y1 : self.y2, self.x1 : self.x2] 

def getBoxes(net , frame, conf_threshold=0.7):
    frameDnn = frame.copy()
    frameHeight = frameDnn.shape[0]
    frameWidth = frameDnn.shape[1]
    blob = cv2.dnn.blobFromImage(frameDnn, 1.0, (300, 300), [104, 117, 123], True, False)
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append(Box(x1, y1, x2, y2))
            #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    return bboxes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Camera app.")
    parser.add_argument('--cam_id', type=int, default=0, help='Input stream ID.')
    parser.add_argument('--width', type=int, default=640, help='Input stream width.')
    parser.add_argument('--heigth', type=int, default=480, help='Input stream heigth.')
    args = parser.parse_args()

    if DNN == 'TF':
        modelFile = os.path.sep.join(["face-detection_model", "opencv_face_detector_uint8.pb"])
        configFile = os.path.sep.join(["face-detection_model", "opencv_face_detector.pbtxt"])
        net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)
    else:
        modelFile = os.path.sep.join(["face-detection_model", "res10_300x300_ssd_iter_140000.caffemodel"])
        configFile = os.path.sep.join(["face-detection_model", "deploy.prototxt"])
        net = cv2.dnn.readNetFromCaffe(modelFile, configFile)

    cap = cv2.VideoCapture(args.cam_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.heigth)

    cropQueue = queue.Queue(10)

    ret, frame = cap.read()
    if (ret == True):
        q = Box(10,10,200,200,156)
       
        while True:
            frame = cv2.flip(frame, 1)
            boxes = getBoxes(net, frame)
            if len(boxes) > 0 :
                crop = boxes[0].crop_image(frame)
                cv2.imshow('crop', crop)
            cv2.imshow("camera_module", frame)
            if cv2.waitKey(10) == 27:
                exitFlag = 1
                break
            ret, frame = cap.read()

    cv2.destroyAllWindows() 
    cv2.VideoCapture(0).release()

