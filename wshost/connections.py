from wshost import exceptions


class Connection:
    def __init__(self, conn):
        self.conn = conn

    def readline(self, buffer):
        data = bytes()
        while True:
            try:
                char = self.conn.recv(1)        
            except:
                raise exceptions.BadRequest
            
            if not char:
                raise exceptions.NoData
            
            data += char
            if data.endswith(b"\r\n"):
                return data[:-2]
            
            if len(data) == buffer:
                raise exceptions.OverBuffer
            
    def read(self, buffer, buffer_size):
        body = bytes()

        while len(body) != buffer:
            if (len(body) + buffer_size) > buffer:
                try:
                    body += self.conn.recv(buffer - len(body))
                except:
                    raise exceptions.BadRequest
                
            else:
                try:
                    body += self.conn.recv(buffer_size)
                except:
                    raise exceptions.BadRequest
                
        return body
