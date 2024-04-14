from wshost import connections
from wshost import exceptions
from wshost import encodings
from wshost import responses
from wshost import payloads
from wshost import statuses
from wshost import cookies
from wshost import headers
from wshost import errors
from wshost import etags
import mimetypes
import traceback
import fnmatch
import os


HTTP_METHOD = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]


def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def request_handle(request, no_etag=False):
    method = request["method"]
    path = request["path"]
    config = request["config"]
    root = os.path.join(config.root_directory, config.html_directory).replace("\\", "/")
    file = path.split("/")
    filename = file[-1]
    
    if method in ["GET", "HEAD"]:
        try:
            if not filename:
                path = f"{path}/index.html"
                filename = "index.html"

            elif os.path.isdir(f"{root}{path}"):
                content = b""
                return responses.Redirect(f"{path}/")

            if not os.path.exists(f"{root}{path}"):
                return responses.Error(statuses.NOT_FOUND)

            content = read(f"{root}{path}")
            content_type = mimetypes.guess_type(filename)[0]

            if content_type == None:
                content_type = "text/plain"

            if not no_etag:
                last_modified = [("Last-Modified", etags.get_last_modified(f"{root}{path}"))]
                etag = etags.generate_etag(content)

                if etags.check_etag(request, etag):
                    return responses.not_modified(content, last_modified)
            
            else:
                last_modified = []
            
        except PermissionError:
            return responses.Error(statuses.NOT_FOUND)

        try:
            content = content.decode()
        except UnicodeDecodeError:
            pass

        return responses.Response(content, header=last_modified, content_type=content_type, etag=(not no_etag), no_content=(method == "head"))
    else:
        return responses.Error(statuses.METHOD_NOT_ALLOWED)
    
class Request:
    def __init__(self, conn, addr, config):
        self.conn = conn
        self.addr = addr
        self.config = config

        self.connection = connections.Connection(conn)

        self.request = {"conn": conn, "addr": addr, "ip": addr[0], "config": config}

    def request_handle(self):
        try:
            try:
                first_line = self.connection.readline(self.config.buffer_size)
            
            except exceptions.OverBuffer:
                return self.generate_error_message(statuses.URI_TOO_LARGE)

            if not first_line:
                return True
            
            try:
                method, path, protocol, protocol_version = headers.first_line_decode(first_line.decode())
                if method not in HTTP_METHOD:
                    raise exceptions.BadRequest

                path, parameter = headers.path_decode(path)
            except:
                raise exceptions.BadRequest

            header = bytes()

            while True:
                try:
                    line = self.connection.readline(self.config.buffer_size - len(header))
                    if not line:
                        break

                    header += line + b"\r\n"

                except exceptions.OverBuffer:
                    return self.generate_error_message(statuses.REQUEST_HEADER_FIELDS_TOO_LARGE)
                
            header = headers.decode(header)

            self.request = {
                "conn": self.conn,
                "addr": self.addr,
                "ip": self.addr[0],
                "header": header,
                "method": method,
                "protocol": protocol,
                "protocol_version": protocol_version,
                "path": path,
                "parameter": parameter,
                "body": bytes(),
                "config": self.config
            }

            try:
                self.get_payload(header)
            except exceptions.OverBuffer:
                return self.generate_error_message(statuses.CONTENT_TOO_LARGE)

            return self.handle_request()
        
        except exceptions.BadRequest:
            try:
                return self.generate_error_message(statuses.BAD_REQUEST)
            except:
                return False
            
        except OSError:
            return False
        
        except exceptions.NoData:
                return False

        except:
            if self.config.debug:
                traceback.print_exc()

            return self.generate_error_message(statuses.INTERNAL_SERVER_ERROR)
        
    def get_payload(self, header):
        if "Content-Length" in header:
            try:
                upload_size = int(header["Content-Length"])
            except:
                raise exceptions.BadRequest
                
            if upload_size > self.config.max_upload_size:
                raise exceptions.OverBuffer
            else:
                self.request["body"] = self.connection.read(upload_size, self.config.buffer_size)

        if "Transfer-Encoding" in header:
            if header["Transfer-Encoding"] == "chunked":
                try:
                    self.request["body"] = encodings.read_chunked(self.conn, self.config.max_upload_size)

                except:
                    raise exceptions.BadRequest
                
        if "Content-Type" in header:
            if header["Content-Type"] == "application/x-www-form-urlencoded":
                self.request["form"] = payloads.form_decode(self.request)

            if list(headers.header_decode(header["Content-Type"]))[0] == "multipart/form-data":
                self.request["form"] = payloads.multipart_decode(self.request)

        try:
            self.request["cookie"] = cookies.get_cookie(self.request)
        except:
            raise exceptions.BadRequest
        
    def handle_request(self):
        for x in self.config.route:
            if fnmatch.fnmatch(self.request["path"], x):
                if callable(self.config.route[x]):
                    response = self.config.route[x](self.request)
                else:
                    if self.request["method"] not in ["GET", "HEAD", "POST"]:
                        return self.generate_error_message(statuses.METHOD_NOT_ALLOWED)
                    
                    response = self.config.route[x]

                if not (((type(response) == responses.Error) and (response.error == statuses.NOT_FOUND) and response.passing) or response == None):
                    return self.response_handle(response)
                
        return self.response_handle(request_handle(self.request))
        
    def generate_error_message(self, error):
        return self.response_handle(errors.generate_error_message(error, self.request), status=error)
    
    def response_handle(self, response, status=statuses.OK):
        connection = ("header" in self.request) and ("Connection" in self.request["header"]) and (self.request["header"]["Connection"] == "keep-alive")
        if type(response) in [str, bytes, list, dict]:
            return self.response_handle(responses.Response(response), status=status)
        
        elif type(response) == bool:
            return response
        
        elif type(response) == responses.RawResponse:
            self.conn.sendall(response.response)
            return response.connection and connection

        elif type(response) == responses.Route:
            self.request["path"] = response.path
            return self.response_handle(request_handle(self.request, no_etag=(status != statuses.OK)), status=status)
        
        elif type(response) == responses.Redirect:
            return self.response_handle(responses.Response(
                "",
                header=response.header + [("Location", response.url), ("Content-Length", "")],
                status=response.status
            ),
            self.request, status=status)
        
        elif type(response) == responses.Error:
            return self.generate_error_message(response.error)
        
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
                    no_content=response.no_content or (self.request["method"] == "HEAD")
                ))

                return response.connection and connection
            return False
        
        else:
            return False
