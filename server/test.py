import cv2
import numpy as np
import dlib

cap = cv2.VideoCapture(0)
net = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')

while True:
    ret, frame = cap.read()
    dets = net(frame, 1)
    for k, d in enumerate(dets):
        shape = sp(frame, d)
        print(shape.part(0))
        for i in range(0, 68):
            #print(shape.part(i))
            #print(shape.part(i).x," ", shape.part(i).y)
            cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 2, (0,0,255))

    cv2.imshow("test dlib shape detector", frame)
    if cv2.waitKey(10) == 27:
        break