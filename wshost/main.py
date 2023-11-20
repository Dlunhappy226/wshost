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
        while True:
            if self.request_handle(conn, addr) == False:
                conn.close()
                break

    def request_handle(self, conn, addr):
        try:
            script_found = False

            request = conn.recv(65537)

            if request == b"":
                return False

            if request == b"\r\n":
                return
            
            if len(request) > 65536:
                conn.sendall(files.generate_error_message(headers.REQUEST_HEADER_FIELDS_TOO_LARGE, self.config.error_html))
                return

            header = headers.decode(request)
            method, path, protocol = headers.head_decode(header[0])
            request_path, parameter = headers.path_decode(path)

            if protocol.lower() != "http/1.1":
                conn.sendall(files.generate_error_message(headers.BAD_REQUEST, self.config.error_html))
                return False

            for key in self.config.routing:
                if fnmatch.fnmatch(request_path, key):
                    try:
                        response = self.config.routing[key]({"conn": conn, "addr": addr, "content": request})
                        return response
                    except:
                        if self.config.debug:
                            traceback.print_exc()
                        response = files.generate_error_message(headers.INTERNAL_SERVER_ERROR, self.config.error_html)
                        conn.sendall(response)
                        
                    script_found = True
                    break

            if not script_found:
                try:
                    response = files.handle_request(method, request_path, self.config.root_directory, self.config.error_html)
                except:
                    if self.config.debug:
                        traceback.print_exc()
                    response = files.generate_error_message(headers.INTERNAL_SERVER_ERROR, self.config.error_html)
                conn.sendall(response)
        except:
            response = files.generate_error_message(headers.BAD_REQUEST, self.config.error_html)
            conn.sendall(response)
            return False
        return
