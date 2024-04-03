from wshost import connections
from wshost import exceptions
from wshost import responses
from wshost import encodings
from wshost import payloads
from wshost import statuses
from wshost import cookies
from wshost import headers
from wshost import errors
import traceback
import fnmatch


class Clients:
    def __init__(self, conn, addr, config):
        self.conn = conn
        self.addr = addr
        self.config = config
        self.connection = connections.Connection(conn)

    def run_forever(self):
        while self.request_handle():
            pass

        self.conn.close()
    
    def request_handle(self):
        request = {"conn": self.conn, "addr": self.addr, "ip": self.addr[0], "config": self.config}

        try:
            try:
                first_line = self.connection.readline(self.config.buffer_size)
            
            except exceptions.OverBuffer:
                return self.generate_error_message(statuses.URI_TOO_LARGE, request)

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
                    line = self.connection.readline(self.config.buffer_size - len(header))
                    if line == b"":
                        break

                    header += line + b"\r\n"

                except exceptions.OverBuffer:
                    return self.generate_error_message(statuses.REQUEST_HEADER_FIELDS_TOO_LARGE, request)
                
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
                    return self.generate_error_message(statuses.CONTENT_TOO_LARGE, request)
                else:
                    body = self.connection.read(upload_size, self.config.buffer_size)

            if "Transfer-Encoding" in header:
                if header["Transfer-Encoding"] == "chunked":
                    try:
                        body = encodings.read_chunked(request)
                    
                    except exceptions.OverBuffer:
                        return self.generate_error_message(statuses.CONTENT_TOO_LARGE, request)
                    
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
                return self.generate_error_message(statuses.BAD_REQUEST, request)
            except:
                return False
            
        except OSError:
            return False
        
        except exceptions.NoData:
                return False

        except:
            if self.config.debug:
                traceback.print_exc()

            return self.generate_error_message(statuses.INTERNAL_SERVER_ERROR, request)
        
    def handle_request(self, request):
        for x in self.config.route:
            if fnmatch.fnmatch(request["path"], x):
                if callable(self.config.route[x]):
                    response = self.config.route[x](request)
                else:
                    response = self.config.route[x]

                if not (((type(response) == responses.Error) and (response.error == statuses.NOT_FOUND) and response.passing) or response == None):
                    return self.response_handle(response, request)
                
        return self.response_handle(responses.request_handle(request), request)
        
    def generate_error_message(self, error, request):
        return self.response_handle(errors.generate_error_message(error, request), request, error)
    
    def response_handle(self, response, request, status=statuses.OK):
        connection = ("header" in request) and ("Connection" in request["header"]) and (request["header"]["Connection"] == "keep-alive")
        if type(response) in [str, bytes, list, dict]:
            self.conn.sendall(responses.encode_response(response, connection=connection, status=status))
            return connection
        
        elif type(response) == bool:
            return response
        
        elif type(response) == responses.Response:
            if type(response.content) in [str, bytes, list, dict]:
                if status != statuses.OK and response.status == statuses.OK:
                    response.status = status

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
            return self.response_handle(responses.request_handle(request, no_etag=(status != statuses.OK)), request, status=status)
        
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
        