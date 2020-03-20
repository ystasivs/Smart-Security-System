import argparse
import dlib
import json
import glob
import os


parser = argparse.ArgumentParser(description="Create face info")
parser.add_argument(
    '-p',
    '--path',
    type=str,
    default='faces',
    help='Specify path to faces'
)
parser.add_argument(
    '-o',
    '--output',
    type=str,
    default='face_data',
    help='Specify output name'
)
parser.add_argument(
        '-sp',
        '--shape_predictor',
        type=str,
        default='shape_predictor_5_face_landmarks.dat',
        help='Set shape predictor path')
parser.add_argument(
        '-fr',
        '--face_recognition',
        type=str,
        default='dlib_face_recognition_resnet_model_v1.dat',
        help='Set face recognizer path'
    )
args = parser.parse_args()

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(args.shape_predictor)
facerec = dlib.face_recognition_model_v1(args.face_recognition)
face_dict = {}
for f in glob.glob(os.path.join(args.path, "*.jpg")):
    print("Processing file: {}".format(f))
    img = dlib.load_rgb_image(f)
    #print(img.shape)
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
        print(d)
        shape = sp(img, d)
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        vector = [x for x in face_descriptor]
        #print(face_descriptor[0])
        face_dict.update({f[len(args.path) +1 : len(f)-4] : vector})
       

json = json.dumps(face_dict)
f = open(f'{args.output}.json',"w")
f.write(json)
f.close()