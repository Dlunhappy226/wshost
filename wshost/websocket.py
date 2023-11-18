from wshost import headers
import hashlib
import base64
import struct


fin = 0x80
opcode = 0x0f
length = 0x7f
len_16 = 0x7e
len_64 = 0x7f

opcode_continuation = 0x0
opcode_text = 0x1
opcode_binary = 0x2
opcode_close = 0x8
opcode_ping = 0x9
opcode_pong = 0xA
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

id = 0

class websocket:
    def __init__(self, conn, request, max_size=1000000):
        global id
        self.conn = conn
        self.id = id
        id = id + 1
        self.max_size = max_size
        header = headers.decode(request)
        if "Sec-WebSocket-Key" not in header[1]:
            response = headers.encode("400 Bad Request", []).encode() + b"400 Bad Request"
            conn.sendall(response)
            return None
        
        websocket_key = self.generate_key(header[1]["Sec-WebSocket-Key"])
        response = headers.encode("101 Switching Protocols", [
            ("Upgrade", "websocket"),
            ("Connection", "Upgrade"),
            ("Sec-WebSocket-Accept", websocket_key)
        ])
        conn.sendall(response.encode())

    def generate_key(self, key):
        key_hash = hashlib.sha1((key + GUID).encode())
        key_encode = base64.b64encode(key_hash.digest())
        return key_encode.decode()
    
    def encode(self, content, op_code):
        header = bytearray()
        content_length = len(content)
        
        if content_length <= 125:
            header.append(fin | op_code)
            header.append(content_length)
        elif 126 <= content_length <= 65535:
            header.append(fin | op_code)
            header.append(len_16)
            header.extend(struct.pack(">H", content_length))
        elif content_length < 18446744073709551616:
            header.append(fin | op_code)
            header.append(len_64)
            header.extend(struct.pack(">Q", content_length))
        else:
            return
        
        return header + content
    
    def decode(self, content):
        op_code = content[0] & opcode
        content_length = content[1] & length

        if content_length == 126:
            content_length = struct.unpack(">H", content[3:5])[0]
            masks = content[6:10]
            content_read = content[10:10 + content_length]
        elif content_length == 127:
            content_length = struct.unpack(">Q", content[3:11])[0]
            masks = content[12:16]
            content_read = content[16:16 + content_length]
        else:
            masks = content[2:6]
            content_read = content[6:6+content_length]

        message = bytearray()
        for x in content_read:
            x ^= masks[len(message) % 4]
            message.append(x)

        return message, op_code
    
    def send(self, content, op_code):
        self.conn.sendall(self.encode(content, op_code))

    def close(self):
        self.sendall("", opcode_close)
        self.conn.close()
    
    def run_forever(self):
        while True:
            try:
                message = self.conn.recv(self.max_size)
                content, op_code = self.decode(message)

                if op_code == opcode_text:
                    self.onmessage(self, content)
                elif op_code == opcode_close:
                    self.conn.close()
                    self.onclose(self)
                    break
                elif op_code == opcode_ping:
                    self.send(content, opcode_pong)

            except:
                self.conn.close()
                self.onclose()
                break

    def onmessage(self, message):
        pass

    def onclose(self):
        pass
