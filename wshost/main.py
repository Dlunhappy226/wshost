from wshost import headers
from wshost import files
import traceback
import threading
import fnmatch
import socket
import sys


class app:
    def __init__(self, config):
        print("Starting WSHost")
        self.config = config

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        server.bind((config.host, config.port))
        server.listen()

        address = server.getsockname()

        print("WSHost listening {}:{}".format(address[0], address[1],))

        self.main(server)

        server.close()
        sys.exit()

    def main(self, server):
        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=self.client_handler, args=(conn, addr))
            client_thread.start()

    def client_handler(self, conn, addr):
        request = conn.recv(self.config.socket_max_receive_size)
        script_found = False
        try:
            header = headers.decode(request)
            head = header[0].split(" ")
            head[1] = head[1].partition("?")[0]
            for key in self.config.routing:
                if fnmatch.fnmatch(head[1], key):
                    try:
                        self.config.routing[key]({"conn": conn, "addr": addr, "content": request})
                    except:
                        traceback.print_exc()
                        error_message = self.config.error_html.format("500 Internal Server Error", "500 Internal Server Error").encode()
                        response = headers.encode("500 Internal Server Error", [
                            ("Content-Length", len(error_message)),
                            ("Content-Type", "text/html")
                        ]).encode() + error_message
                        conn.sendall(response)
                    script_found = True
                    break
            if not script_found:
                try:
                    response = files.handle_request(head, self.config.root_directory, self.config.error_html)
                except:
                    traceback.print_exc()
                    error_message = self.config.error_html.format("500 Internal Server Error", "500 Internal Server Error").encode()
                    response = headers.encode("500 Internal Server Error", [
                        ("Content-Length", len(error_message)),
                        ("Content-Type", "text/html")
                    ]).encode() + error_message
                    conn.sendall(response)
        except:
            error_message = self.config.error_html.format("400 Bad Request", "400 Bad Request").encode()
            response = headers.encode("400 Bad Request", [
                ("Content-Length", len(error_message)),
                ("Content-Type", "text/html")
            ]).encode() + error_message
        if not script_found:
            conn.sendall(response)
        conn.close()
