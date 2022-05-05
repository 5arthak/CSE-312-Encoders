import socketserver
import sys

from util.router import Router
from util.request import Request
from util.static_paths import add_paths as static_paths
from util.form_paths import add_paths as form_paths
from util.login_paths import add_paths as login_paths
import util.websockets as ws


class MyTCPHandler(socketserver.BaseRequestHandler):
    ws_connections = {}
    ws_conn_list = []
    ws_other = {}
    def __init__(self, request, client_address, server):
        self.router = Router()
        ws.add_paths(self.router)
        form_paths(self.router)
        login_paths(self.router)
        static_paths(self.router)
        super().__init__(request, client_address, server)

    def handle(self):
        content_length = 2048
        all_data = b''
        while len(all_data) < content_length: # while we haven't read all content-length
            received_data = self.request.recv(2048) #bit array at most 2kb bytes
            if len(received_data) == 0:
                return
            print("\n- - - received data - - -")
            print(received_data)
            print("- - - end of data - - -")
            if len(all_data) == 0:
                request = Request(received_data)
                content_length = int(request.headers.get("Content-Length", 0))
                all_data += request.body
                header = received_data.split(b'\r\n\r\n')[0]

            else: all_data += received_data

        # print(header)
        self.router.handle_request(Request(header + b'\r\n\r\n' + all_data), self)

        # For docker, prints the buffer
        sys.stdout.flush()
        sys.stderr.flush()


if __name__ == "__main__":
    host, port = "0.0.0.0", 8080

    with socketserver.ThreadingTCPServer((host, port), MyTCPHandler) as server:

        print("Listening on port " + str(port))

        sys.stdout.flush()
        sys.stderr.flush()

        server.serve_forever()