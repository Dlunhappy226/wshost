from wshost import exceptions
from wshost import statuses
from wshost import headers
import traceback
import hashlib
import base64
import struct


FIN = 0x80
OPCODE = 0x0f
LENGTH = 0x7f
LEN_16 = 0x7e
LEN_64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

id = 0
clients = []


def sendall(content, except_for="", opcode=OPCODE_TEXT):
    for client in clients:
        if client != except_for:
            try:
                client.send(content, opcode=opcode)
            except:
                client.close()


class Websocket:
    def __init__(self, request, max_size=1024*1024, debug=False):
        def onmessage(self, message):
            pass

        def onclose(self):
            pass

        self.conn = request["conn"]
        self.max_size = max_size
        self.debug = debug

        self.onmessage = onmessage
        self.onclose = onclose

        global id
        self.id = id
        id += 1

        self.message = bytes()
        self.opcode = False

        if "Sec-WebSocket-Key" in request["header"]:
            websocket_key = self.generate_key(request["header"]["Sec-WebSocket-Key"])
        else:
            websocket_key = self.generate_key(request["header"]["Sec-Websocket-Key"])

        response = headers.encode(statuses.SWITCHING_PROTOCOLS, [
            ("Upgrade", "websocket"),
            ("Connection", "Upgrade"),
            ("Sec-WebSocket-Accept", websocket_key)
        ])

        self.conn.sendall(response)
        clients.append(self)

    def generate_key(self, key):
        key_hash = hashlib.sha1((key + GUID).encode())
        key_accept = base64.b64encode(key_hash.digest())
        return key_accept.decode()
    
    def encode(self, content, opcode):
        header = bytes([FIN | opcode])
        length = len(content)
        
        if length <= 125:
            header += bytes([length])
        elif 126 <= length <= 65535:
            header += bytes([LEN_16])
            header += struct.pack(">H", length)
        elif length < 18446744073709551616:
            header += bytes([LEN_64])
            header += struct.pack(">Q", length)
        else:
            return
        
        return header + content
    
    def read_bytes(self, buffer):
        data = bytes()
        for x in range(buffer):
            byte = self.conn.recv(1)
            if not byte:
                raise exceptions.NoData
            
            data += byte

        return data
    
    def read(self):
        first_byte = self.read_bytes(1)[0]
        opcode = first_byte & OPCODE
        fin = first_byte >> 7
        length = self.read_bytes(1)[0] & LENGTH

        if length == 126:
            length = struct.unpack(">H", self.read_bytes(2))[0]

        elif length == 127:
            length = struct.unpack(">Q", self.read_bytes(8))[0]

        masks = self.read_bytes(4)

        if length > self.max_size:
            raise exceptions.OverBuffer

        content = self.read_bytes(length)

        data = bytes()

        for x in content:
            x ^= masks[len(data) % 4]
            data += bytes([x])

        return fin, opcode, data
    
    def send(self, content, opcode=OPCODE_TEXT):
        if type(content) == str:
            content = content.encode()
            
        self.conn.sendall(self.encode(content, opcode))

    def close(self):
        self.send("", OPCODE_CLOSE)
        self.conn.close()
        clients.remove(self)
        self.onclose(self)

    def request_handle(self, opcode, content):
        if opcode in [OPCODE_TEXT, OPCODE_BINARY]:
            self.onmessage(self, content)

        elif opcode == OPCODE_CLOSE:
            self.conn.close()
            clients.remove(self)
            self.onclose(self)
            return False
        
        elif opcode == OPCODE_PING:
            self.send(content, OPCODE_PONG)

    def run_forever(self):
        while True:
            try:
                fin, opcode, content = self.read()

                if opcode != OPCODE_CONTINUATION:
                    self.opcode = opcode

                self.message += content
                
                if fin:
                    self.request_handle(self.opcode, self.message)
                    self.message = bytes()
                    self.opcode = False

            except:
                if self.debug:
                    traceback.print_exc()

                self.conn.close()
                clients.remove(self)
                self.onclose(self)
                return False
