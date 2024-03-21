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
        while self.request_handle(self.conn, self.addr):
            pass

        self.conn.close()
    
    def request_handle(self, conn, addr):
        try:
            raw_request = conn.recv(8193)

            if raw_request == b"":
                return False

            if raw_request == b"\r\n":
                return True
            
            request = {"conn": conn, "addr": addr, "ip": addr[0], "content": raw_request, "config": self.config}

            head, header, body = headers.decode(raw_request)
            method, path, protocol = headers.head_decode(head)
            request_path, parameter = headers.path_decode(path)

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

            if "Content-Length" in header:
                upload_size = int(header["Content-Length"])
                if upload_size > self.config.max_upload_size:
                    return self.generate_error_message(headers.PAYLOAD_TOO_LARGE, request)

                else:
                    while len(body) != upload_size:
                        if (len(body) + 8192) > upload_size:
                            body += conn.recv(upload_size - len(body))
                            
                        else:
                            body += conn.recv(8192)

            if "Transfer-Encoding" in header:
                if header["Transfer-Encoding"] == "chunked":
                    body = encoding.read_chunked(request)
                    if body == False:
                        return self.generate_error_message(headers.PAYLOAD_TOO_LARGE, request)

            elif len(raw_request) > 8192:
                return self.generate_error_message(headers.REQUEST_HEADER_FIELDS_TOO_LARGE, request)

            request["body"] = body

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
                return self.response_handle(response, request)
                
            except:
                if self.config.debug:
                    traceback.print_exc()

                return self.generate_error_message(headers.INTERNAL_SERVER_ERROR, request)

        except:
            try:
                return self.generate_error_message(headers.BAD_REQUEST, request)
            except:
                pass

            return False
        
    def response_handle(self, response, request):
        connection = "Connection" in request["header"] and request["header"]["Connection"] == "keep-alive"
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
            self.conn.sendall(responses.encode_response("", response.status, [("Location", response.url)], connection=(response.connection and connection)))
            return response.connection and connection
        
        elif type(response) == responses.Error:
            return self.generate_error_message(response.error, request)
        
        else:
            return False
        
    def generate_error_message(self, error, request):
        return self.response_handle(errors.generate_error_message(error, request), request)
    