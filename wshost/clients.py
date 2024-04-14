from wshost import requests


class Clients:
    def __init__(self, conn, addr, config):
        self.conn = conn
        self.addr = addr
        self.config = config

    def run_forever(self):
        while self.request_handle():
            pass

        self.conn.close()
    
    def request_handle(self):
        request = requests.Request(self.conn, self.addr, self.config)
        return request.request_handle()
