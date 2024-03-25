from wshost import exceptions
from wshost import responses
from wshost import encoding
from wshost import cookies
from wshost import payload
from wshost import headers
from wshost import errors
import traceback
import fnmatch


class Clients:
    def __init__(self, conn, addr, config):
        self.conn = conn
        self.addr = addr
        self.config = config

    def run_forever(self):
        while self.request_handle():
            pass

        self.conn.close()

    def readline(self, buffer=None):
        if buffer is None:
            buffer = self.config.buffer_size

        data = b""
        while True:
            char = self.conn.recv(1)
            if char == b"":
                raise exceptions.NoData
            
            data += char
            if data.endswith(b"\r\n"):
                return data[:-2]
            
            if len(data) == buffer:
                raise exceptions.OverBuffer
    
    def request_handle(self):
        try:
            request = {"conn": self.conn, "addr": self.addr, "ip": self.addr[0], "config": self.config}

            try:
                first_line = self.readline()

            except exceptions.NoData:
                return False
            
            except exceptions.OverBuffer:
                return self.generate_error_message(headers.URI_TOO_LARGE, request)

            if first_line == b"":
                return True
            
            method, path, protocol, protocol_version = headers.first_line_decode(first_line.decode())
            path, parameter = headers.path_decode(path)

            header = b""

            while True:
                try:
                    line = self.readline(buffer=self.config.buffer_size - len(header))
                    if line == b"":
                        break

                    header += line + b"\r\n"
                except exceptions.OverBuffer:
                    return self.generate_error_message(headers.REQUEST_HEADER_FIELDS_TOO_LARGE, request)
                
            header = headers.decode(header)

            request = {
                "conn": self.conn,
                "addr": self.addr,
                "ip": self.addr[0],
                "header": header,
                "method": method,
                "protocol": protocol,
                "protocol_version": protocol_version,
                "path": path,
                "parameter": parameter,
                "config": self.config
            }

            body = b""

            if "Content-Length" in header:
                upload_size = int(header["Content-Length"])
                if upload_size > self.config.max_upload_size:
                    return self.generate_error_message(headers.CONTENT_TOO_LARGE, request)

                else:
                    while len(body) != upload_size:
                        if (len(body) + self.config.buffer_size) > upload_size:
                            body += self.conn.recv(upload_size - len(body))
                            
                        else:
                            body += self.conn.recv(self.config.buffer_size)

            if "Transfer-Encoding" in header:
                if header["Transfer-Encoding"] == "chunked":
                    body = encoding.read_chunked(request)
                    if body == False:
                        return self.generate_error_message(headers.CONTENT_TOO_LARGE, request)

            request["body"] = body

            request["cookie"] = cookies.get_cookie(request)

            if "Content-Type" in header:
                if header["Content-Type"] == "application/x-www-form-urlencoded":
                    request["form"] = payload.form_decode(request)

                if list(headers.header_decode(header["Content-Type"]))[0] == "multipart/form-data":
                    request["form"] = payload.multipart_decode(request)

            for key in self.config.route:
                if fnmatch.fnmatch(path, key):
                    handler = self.config.route[key]

                    try:
                        response = handler(request)
                        if not (type(response) == responses.Error and response.error == headers.NOT_FOUND):
                            return self.response_handle(response, request)
                        
                    except:
                        if self.config.debug:
                            traceback.print_exc()

                        return self.generate_error_message(headers.INTERNAL_SERVER_ERROR, request)
            
            return self.response_handle(responses.request_handle(request), request)

        except:
            try:
                return self.generate_error_message(headers.BAD_REQUEST, request)
            except:
                pass

            return False
        
    def response_handle(self, response, request):
        connection = "header" in request and "Connection" in request["header"] and request["header"]["Connection"] == "keep-alive"
        if type(response) == str or type(response) == bytes or type(response) == list or type(response) == dict:
            self.conn.sendall(responses.encode_response(response, connection=connection))
            return connection
        
        elif type(response) == bool:
            return response
        
        elif type(response) == responses.Response:
            if type(response.content) == str or type(response.content) == bytes or type(response.content) == list or type(response.content) == dict:
                self.conn.sendall(responses.encode_response(response.content, response.status, response.header, connection=(response.connection and connection)))
                return response.connection and connection
            
            return False
        
        elif type(response) == responses.RawResponse:
            self.conn.sendall(response.response)
            return response.connection and connection

        elif type(response) == responses.Route:
            request["path"] = response.path
            self.conn.sendall(responses.request_handle(request).response)
            return response.connection and connection
        
        elif type(response) == responses.Redirect:
            self.conn.sendall(responses.encode_response("", response.status, response.header + [("Location", response.url)], connection=(response.connection and connection)))
            return response.connection and connection
        
        elif type(response) == responses.Error:
            return self.generate_error_message(response.error, request)
        
        else:
            return False
        
    def generate_error_message(self, error, request):
        return self.response_handle(errors.generate_error_message(error, request), request)
    