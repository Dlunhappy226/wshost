from wshost import responses
from wshost import cookies
from wshost import payload
from wshost import headers
from wshost import errors
import traceback
import threading
import fnmatch
import socket
import time
import sys


class App:
    def __init__(self, config):
        if(config.startup):
            print("Starting WSHost")
        self.config = config

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((config.host, config.port))
        server.listen(512)

        address = server.getsockname()

        if(config.startup):
            print("WSHost listening {}:{}".format(address[0], address[1]))

        threading.Thread(target=self.main, args=(server,), daemon=True).start()
        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Exiting")
            server.close()
            sys.exit()


    def main(self, server):
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=self.client_handler, args=(conn, addr), daemon=True).start()
            except:
                return


    def client_handler(self, conn, addr):
        while self.request_handle(conn, addr):
            pass

        conn.close()

    def request_handle(self, conn, addr):
        try:
            def response_handle(response):
                if type(response) == str or type(response) == bytes or type(response) == list or type(response) == dict:
                    conn.sendall(responses.encode_response(response))
                    return True
                
                elif type(response) == bool:
                    return response
                
                elif type(response) == responses.Response:
                    if type(response.content) == str or type(response.content) == bytes or type(response.content) == list or type(response.content) == dict:
                        conn.sendall(responses.encode_response(response.content, response.status, response.header))
                        return response.connection
                    
                    return False
                
                elif type(response) == responses.RawResponse:
                    conn.sendall(response.response)
                    return response.connection

                elif type(response) == responses.Route:
                    request["path"] = response.path
                    conn.sendall(responses.request_handle(request).response)
                    return response.connection
                
                elif type(response) == responses.Redirect:
                    conn.sendall(responses.encode_response("", response.status, [("Location", response.url)]))
                    return response.connection
                
                elif type(response) == responses.Error:
                    return generate_error_message(response.error, request)
                
                else:
                    return False
                
            def generate_error_message(error, request):
                return response_handle(errors.generate_error_message(error, request))
                
            request = {"config": self.config}

            raw_request = conn.recv(8193)

            if raw_request == b"":
                return False

            if raw_request == b"\r\n":
                return True

            head, header, body = headers.decode(raw_request)
            method, path, protocol = headers.head_decode(head)
            request_path, parameter = headers.path_decode(path)

            if "Content-Length" in header:
                upload_size = int(header["Content-Length"])
                if upload_size > self.config.max_upload_size:
                    return generate_error_message(headers.PAYLOAD_TOO_LARGE, request)

                else:
                    while len(body) != upload_size:
                        if (len(body) + 8192) > upload_size:
                            body += conn.recv(upload_size - len(body))
                            
                        else:
                            body += conn.recv(8192)

            elif "Transfer-Encoding" in header:
                if header["Transfer-Encoding"] == "chunked":
                    data = b""

                    def read(buffer, body):
                        read_data = b""
                        for x in range(buffer):
                            if body != b"":
                                read_data += body[:1]
                                body = body[1:]

                            else:
                                read_data += conn.recv(1)
                                
                        return read_data, body

                    while True:
                        chunk_size_str = b""
                        while True:
                            char, body = read(1, body)
                            if char == b"\r":
                                char, body = read(1, body)
                                break

                            chunk_size_str += char

                        chunk_size = int(chunk_size_str, 16)
                        if chunk_size == 0:
                            char, body = read(2, body)
                            break
                        
                        char, body = read(chunk_size, body)
                        data += char
                        char, body = read(2, body)

                    if len(body) > self.config.max_upload_size:
                        return generate_error_message(headers.PAYLOAD_TOO_LARGE, request)
                    
                    body = data

            elif len(raw_request) > 8192:
                return generate_error_message(headers.REQUEST_HEADER_FIELDS_TOO_LARGE, request)

            request = {
                "conn": conn,
                "addr": addr,
                "ip": addr[0],
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

            request["cookie"] = cookies.get_cookie(request)

            if "Content-Type" in header:
                if header["Content-Type"] == "application/x-www-form-urlencoded":
                    request["form"] = payload.form_decode(request)

                if list(headers.header_decode(header["Content-Type"]))[0] == "multipart/form-data":
                    request["form"] = payload.multipart_decode(request)
            
            handler = responses.request_handle

            for key in self.config.route:
                if fnmatch.fnmatch(request_path, key):
                    handler = self.config.route[key]         
                    break

            try:
                response = handler(request)
                return response_handle(response)
                
            except:
                if self.config.debug:
                    traceback.print_exc()

                return generate_error_message(headers.INTERNAL_SERVER_ERROR, request)

        except:
            try:
                return generate_error_message(headers.BAD_REQUEST, request)
            except:
                pass

            return False
