from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse
import argparse
import dlib
import json
import numpy as np
import cv2
import requests

def recognizeFace(im):
    b = dlib.rectangle(0,0,im.shape[1], im.shape[0])
    shape = sp(im, b)
    #print(shape)
    face_chip = dlib.get_face_chip(im, shape)
    face_descriptor = facerec.compute_face_descriptor(face_chip)
    #face_descriptor = facerec.compute_face_descriptor(im, shape)
    vector1 = np.zeros(shape=128)
    for i in range(0, len(face_descriptor)):
        vector1[i] = face_descriptor[i]
    for k in face_data:
        vec_norm = np.linalg.norm(vector1-face_data[k])
        print("vector diff: ", vec_norm)
        
        if vec_norm < 0.6:
            return k
    return 'undefined'
    

class Handler(BaseHTTPRequestHandler):
    def _do_answer(self):
        #print(self.headers)
        data_size = int(self.headers['Content-Length'])
        data_bytes = self.rfile.read(data_size)
        if self.headers['Content-Type'] == "text/html":
            content = "{}".format(data_bytes.decode("utf-8"))
            qs = dict( (k, v if len(v)>1 else v[0] ) 
            for k, v in urllib.parse.parse_qs(content).items())
            if 'check' in qs:
                if qs['check'] == 'Hello from ystasiv':
                    return "Hello ystasiv".encode('utf-8')
                else:
                    return "Who are you?".encode('utf-8')
            return "unknown request".encode('utf-8')
        elif self.headers['Content-Type'] == "image/jpeg":
            array = np.frombuffer(data_bytes, dtype=np.uint8)
            image = cv2.imdecode(array, cv2.IMREAD_COLOR)
            return recognizeFace(image).encode('utf-8')
        elif self.headers['Content-Type'] == "photo":
            print('here')
            result = requests.post(url ="https://api.telegram.org/bot1142650547:AAECZC9zQTiN26s04-EZw6cYn0GZKJN4Z5c/sendPhoto", headers={},
            data={'chat_id': '313115335','caption': 'WARNING. Stranger detected'}, files=[('photo', data_bytes)])
            return "stranger".encode('utf-8')
        else:
            return "unknown request".encode('utf-8')

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self._do_answer())

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run(server_class=ThreadedHTTPServer, handler_class=Handler, addr="", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8282,
        help="Specify the port on which the server listens",
    )
    parser.add_argument(
        '-sp',
        '--shape_predictor',
        type=str,
        default='models/shape_predictor_5_face_landmarks.dat',
        help='Set shape predictor path')
    parser.add_argument(
        '-fr',
        '--face_recognition',
        type=str,
        default='models/dlib_face_recognition_resnet_model_v1.dat',
        help='Set face recognizer path'
    )
    parser.add_argument(
        '--face_data',
        type=str,
        default='face_data.json',
        help='Set face data path'
    )
    args = parser.parse_args()

    sp = dlib.shape_predictor(args.shape_predictor)
    facerec = dlib.face_recognition_model_v1(args.face_recognition)
    with open(args.face_data) as json_file:
        face_data = json.load(json_file)
        json_file.close()
    run(addr=args.listen, port=args.port)
