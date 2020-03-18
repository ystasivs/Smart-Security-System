from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import PIL
from PIL import Image
from io import BytesIO
import urllib.parse
import argparse


class Handler(BaseHTTPRequestHandler):
    def _do_answer(self):
        print(self.headers)
        data_size = int(self.headers['Content-Length'])
        data_bytes = self.rfile.read(data_size)
        if self.headers['Content-Type'] == "text/html":
            print('hello')
            content = "{}".format(data_bytes.decode("utf-8"))
            qs = dict( (k, v if len(v)>1 else v[0] ) 
            for k, v in urllib.parse.parse_qs(content).items())
            if 'check' in qs:
                if qs['check'] == 'Hello from ystasiv':
                    return "Hello ystasiv".encode('utf-8')
                else:
                    return "Who are you?".encode('utf-8')
            return "".encode('utf-8')
        elif self.headers['Content-Type'] == "image/jpeg":
            print('right place')
            data_size = int(self.headers['Content-Length'])
            print(data_size)
            #data_bytes = self.rfile.read(data_size)
            #im = Image.open(BytesIO(data_bytes))
            #im.save('1.jpg')
            print('save')
            return "stasiv".encode('utf-8')
        else:
            return "unknown".encode('utf-8')

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
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
