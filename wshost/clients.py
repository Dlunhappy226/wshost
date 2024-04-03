from wshost import exceptions
from wshost import responses
from wshost import encodings
from wshost import cookies
from wshost import payloads
from wshost import headers
from wshost import errors
from wshost import status
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
            try:
                char = self.conn.recv(1)        
            except:
                raise exceptions.BadRequest
            
            if char == b"":
                raise exceptions.NoData
            
            data += char
            if data.endswith(b"\r\n"):
                return data[:-2]
            
            if len(data) == buffer:
                raise exceptions.OverBuffer
    
    def request_handle(self):
        request = {"conn": self.conn, "addr": self.addr, "ip": self.addr[0], "config": self.config}

        try:
            try:
                first_line = self.readline()
            
            except exceptions.OverBuffer:
                return self.generate_error_message(status.URI_TOO_LARGE, request)

            if first_line == b"":
                return True
            
            try:
                method, path, protocol, protocol_version = headers.first_line_decode(first_line.decode())
                path, parameter = headers.path_decode(path)
            except:
                raise exceptions.BadRequest

            header = b""

            while True:
                try:
                    line = self.readline(buffer=self.config.buffer_size - len(header))
                    if line == b"":
                        break

                    header += line + b"\r\n"

                except exceptions.OverBuffer:
                    return self.generate_error_message(status.REQUEST_HEADER_FIELDS_TOO_LARGE, request)
                
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
                try:
                    upload_size = int(header["Content-Length"])
                except:
                    raise exceptions.BadRequest
                
                if upload_size > self.config.max_upload_size:
                    return self.generate_error_message(status.CONTENT_TOO_LARGE, request)

                else:
                    while len(body) != upload_size:
                        if (len(body) + self.config.buffer_size) > upload_size:
                            try:
                                body += self.conn.recv(upload_size - len(body))
                            except:
                                raise exceptions.BadRequest
                            
                        else:
                            try:
                                body += self.conn.recv(self.config.buffer_size)
                            except:
                                raise exceptions.BadRequest

            if "Transfer-Encoding" in header:
                if header["Transfer-Encoding"] == "chunked":
                    try:
                        body = encodings.read_chunked(request)
                    
                    except exceptions.OverBuffer:
                        return self.generate_error_message(status.CONTENT_TOO_LARGE, request)
                    
                    except:
                        raise exceptions.BadRequest

            request["body"] = body

            try:
                request["cookie"] = cookies.get_cookie(request)
            except:
                raise exceptions.BadRequest

            if "Content-Type" in header:
                if header["Content-Type"] == "application/x-www-form-urlencoded":
                    request["form"] = payloads.form_decode(request)

                if list(headers.header_decode(header["Content-Type"]))[0] == "multipart/form-data":
                    request["form"] = payloads.multipart_decode(request)

            self.handle_request(request)
        
        except exceptions.BadRequest:
            try:
                return self.generate_error_message(status.BAD_REQUEST, request)
            except:
                return False
            
        except OSError:
            return False
        
        except exceptions.NoData:
                return False

        except:
            if self.config.debug:
                traceback.print_exc()

            return self.generate_error_message(status.INTERNAL_SERVER_ERROR, request)
        
    def handle_request(self, request):
        for x in self.config.route:
            if fnmatch.fnmatch(request["path"], x):
                if callable(self.config.route[x]):
                    response = self.config.route[x](request)
                else:
                    response = self.config.route[x]

                if not ((type(response) == responses.Error and response.error == status.NOT_FOUND and response.passing) or response == None):
                    return self.response_handle(response, request)
                
        return self.response_handle(responses.request_handle(request), request)
        
    def generate_error_message(self, error, request):
        return self.response_handle(errors.generate_error_message(error, request), request)
    
    def response_handle(self, response, request):
        connection = "header" in request and "Connection" in request["header"] and request["header"]["Connection"] == "keep-alive"
        if type(response) == str or type(response) == bytes or type(response) == list or type(response) == dict:
            self.conn.sendall(responses.encode_response(response, connection=connection))
            return connection
        
        elif type(response) == bool:
            return response
        
        elif type(response) == responses.Response:
            if type(response.content) == str or type(response.content) == bytes or type(response.content) == list or type(response.content) == dict:
                self.conn.sendall(responses.encode_response(
                    response.content,
                    status=response.status,
                    header=response.header,
                    connection=(response.connection and connection),
                    content_type=response.content_type,
                    etag=response.etag,
                    no_content=response.no_content
                ))
                return response.connection and connection
            
            return False
        
        elif type(response) == responses.RawResponse:
            self.conn.sendall(response.response)
            return response.connection and connection

        elif type(response) == responses.Route:
            request["path"] = response.path
            return self.response_handle(responses.request_handle(request), request)
        
        elif type(response) == responses.Redirect:
            self.conn.sendall(responses.encode_response(
                "",
                status=response.status,
                header=response.header + [("Location", response.url), ("Content-Length", "")],
                connection=(response.connection and connection)
            ))

            return response.connection and connection
        
        elif type(response) == responses.Error:
            return self.generate_error_message(response.error, request)
        
        else:
            return False
        