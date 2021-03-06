import cv2
import threading
import argparse
import numpy as np
import os
import time
import requests
import sys
from Box import Box
import random
import dlib
import subprocess as sps



exitFlag = 0
DNN = 'dlib'
dlib_scale = 0

class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print("Starting server comunication thread")
        sendToServer()
        print("Exiting server communication thread")


def sendToServer():
    while not exitFlag:
        for face in faceBoxes:
            if face.label == "undefined":
                crop = face.crop_image(frame)
                ret,jpeg = cv2.imencode('.jpg', crop)
                imgdata = jpeg.tobytes()
                #print(time.time() - face.sess_start_time)
                if time.time() - face.sess_start_time < 8:
                    headers = {"Content-Type" :"image/jpeg"}
                else:
                    headers = {"Content-Type" :"photo"}
                response = requests.post(
                    url = f'http://{args.ip}:{args.port}',
                    data =  imgdata,
                    headers = headers
                )
                face.label = response.text
        time.sleep(1)



def getBoxes(net , frame, conf_threshold=0.7):
    bboxes = []
    if DNN == 'dlib':
        dets = net(frame, dlib_scale)
        for k, d in enumerate(dets):
            bboxes.append([d.left(), d.top(), d.right(), d.bottom()])
    else:
        frameDnn = frame.copy()
        frameHeight = frameDnn.shape[0]
        frameWidth = frameDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameDnn, 1.0, (300, 300), [104, 117, 123], True, False)
        net.setInput(blob)
        detections = net.forward()
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([x1, y1, x2, y2])
    return bboxes

def drawBoxes(Boxes, frame):
    for box in Boxes:
        box.drawBox(frame)
        box.updateStatus = False

def processBox(faceBoxes, bboxes):
    newFaceBoxes = []
    for face in faceBoxes:
        for box in bboxes:
            if face.isNextFrame(box):
                face.updateCoords(box)
                face.updateStatus = True
                bboxes.remove(box)
                newFaceBoxes.append(face)
    for box in bboxes:
        newFaceBoxes.append(Box(box, random.randint(1, 9999999)))
    return newFaceBoxes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Camera app.")
    parser.add_argument('--cam_id', type=int, default=0, help='Input stream ID.')
    parser.add_argument('--width', type=int, default=640, help='Input stream width.')
    parser.add_argument('--heigth', type=int, default=480, help='Input stream heigth.')
    parser.add_argument('--ip', type=str, default='192.168.1.104', help='Specify the IP address on which the server listens')
    parser.add_argument('--port', type=str, default='8282', help='Specify the port on which the server listens')
    args = parser.parse_args()

    try:
        print('[INFO] Loading model')
        if DNN == 'dlib':
            net = dlib.get_frontal_face_detector()
        elif DNN == 'TF':
            modelFile = os.path.sep.join(["face-detection_model", "opencv_face_detector_uint8.pb"])
            configFile = os.path.sep.join(["face-detection_model", "opencv_face_detector.pbtxt"])
            net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)
        else:
            modelFile = os.path.sep.join(["face-detection_model", "res10_300x300_ssd_iter_140000.caffemodel"])
            configFile = os.path.sep.join(["face-detection_model", "deploy.prototxt"])
            net = cv2.dnn.readNetFromCaffe(modelFile, configFile)
    except Exception:
        sys.exit('[ERROR] Failed to load model')
    print('[INFO] Model successfuly loaded')

    # try:
    #     print('[INFO] Connecting to server')
    #     response = requests.post(
    #         url = f'http://{args.ip}:{args.port}',
    #         data = {'check': 'Hello from ystasiv'},
    #         headers = {"Content-Type" :"text/html"}
    #     )
    #     if response.text != "Hello ystasiv":
    #         raise RuntimeError
    # except Exception:
    #     sys.exit('[ERROR] Failed to connect to server')

    print('[INFO] Successfully connected to server')

    print('[INFO] Setting up camera')

    cap = cv2.VideoCapture(args.cam_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.heigth)


    ffmpeg = 'ffmpeg'
    dimension = '640x480'
    f_format = 'bgr24'
    command = [ffmpeg,
           '-y',
           '-f', 'rawvideo',
           '-vcodec','rawvideo',
           '-video_size', dimension,
           '-pix_fmt', 'bgr24',
           '-r', '15',
           '-i', '-',
           '-an',
           '-vcodec', 'libx264',
           '-f', 'rtp',
           'rtp://192.151.150.42:8004' ]
    proc = sps.Popen(command, stdin=sps.PIPE, stderr=sps.PIPE)


    print('[INFO] Stream started')
    random.seed(33)
    faceBoxes = []
    ret, frame = cap.read()
    #thread = ServerThread()
    #thread.start()
    if (ret == True):
        while True:
            t = time.time()
            frame = cv2.flip(frame, 1)
            bboxes = getBoxes(net, frame)
            faceBoxes = processBox(faceBoxes, bboxes)
            drawBoxes(faceBoxes, frame)
            cv2.imshow("camera_module", frame)
            proc.stdin.write(frame.tostring())
            if cv2.waitKey(10) == 27:
                exitFlag = 1
                break
            ret, frame = cap.read()
            #print("FPS: ", 1.0/(time.time() - t))

    cv2.destroyAllWindows()
    cv2.VideoCapture(0).release()
    thread.join()
    #313115335


