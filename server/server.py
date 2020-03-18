from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import PIL
from PIL import Image
from io import BytesIO
import argparse

class Handler(BaseHTTPRequestHandler):
    def _do_answer(self):
        data_size = int(self.headers['Content-Length'])
        data_bytes = self.rfile.read(data_size)
        im = Image.open(BytesIO(data_bytes))
        im.save('1.jpg')
        return "yes".encode('utf-8')

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
