from wshost import responses
from wshost import headers
import traceback
import threading
import fnmatch
import socket
import sys


class App:
    def __init__(self, config):
        if(config.startup):
            print("Starting WSHost")
        self.config = config

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        server.bind((config.host, config.port))
        server.listen()

        address = server.getsockname()

        if(config.startup):
            print("WSHost listening {}:{}".format(address[0], address[1]))

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
                return

    def request_handle(self, conn, addr):
        try:
            raw_request = conn.recv(65537)

            if raw_request == b"":
                return False

            if raw_request == b"\r\n":
                return
            
            if len(raw_request) > 65536:
                conn.sendall(responses.generate_error_message(headers.REQUEST_HEADER_FIELDS_TOO_LARGE, self.config.error_html))
                return

            head, header, body = headers.decode(raw_request)
            method, path, protocol = headers.head_decode(head)
            request_path, parameter = headers.path_decode(path)
            request = {
                "conn": conn,
                "addr": addr,
                "content": raw_request,
                "head": head,
                "header": header,
                "body": body,
                "method": method,
                "protocol": protocol,
                "path": request_path,
                "parameter": parameter,
                "config": self.config
            }
            
            handler = responses.handle_request

            for key in self.config.route:
                if fnmatch.fnmatch(request_path, key):
                    handler = self.config.route[key]         
                    break

            try:
                response = handler(request)
                
                if type(response) == str:
                    conn.sendall(responses.encode_response(response))
                    return True
                
                elif type(response) == bytes:
                    conn.sendall(responses.encode_binary_response(response))
                    return True
                
                elif type(response) == bool:
                    return response
                
                elif type(response) == responses.response:
                    if type(response.content) == str:
                        response = responses.encode_response(response.content, response.status, response.header)
                    elif type(response.content) == bytes:
                        response = responses.encode_binary_response(response.content, response.status, response.header)
                    conn.sendall(response)
                    return True
                
                elif type(response) == responses.raw_response:
                    conn.sendall(response.response)
                    return True

                elif type(response) == responses.route:
                    request["path"] = response.path
                    conn.sendall(responses.handle_request(request).response)
                    return True
                
                elif type(response) == responses.redirect:
                    conn.sendall(responses.encode_response("", response.status, [("Location", response.url)]))
                    return True
                
                elif type(response) == responses.error:
                    conn.sendall(responses.generate_error_message(response.error, self.config.error_html))
                    return True
                
                else:
                    return False
                
            except:
                if self.config.debug:
                    traceback.print_exc()
                response = responses.generate_error_message(headers.INTERNAL_SERVER_ERROR, self.config.error_html)
                try:
                    conn.sendall(response)
                except:
                    pass
                
            return

        except:
            response = responses.generate_error_message(headers.BAD_REQUEST, self.config.error_html)

            try:
                conn.sendall(response)

            except:
                pass

            return False
