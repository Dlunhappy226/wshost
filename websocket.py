import hashlib
import headers
import base64
import struct
import config

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
    def __init__(self, conn, request):
        global id
        self.conn = conn
        self.id = id
        id = id + 1
        header = headers.decode(request)
        if "Sec-WebSocket-Key" not in header[1]:
            response = headers.encode("400 Bad Request", []).encode() + b"400 Bad Request"
            conn.sendall(response)
            return None
        
        websocketKey = self.generateKey(header[1]["Sec-WebSocket-Key"])
        response = headers.encode("101 Switching Protocols", [
            ("Upgrade", "websocket"),
            ("Connection", "Upgrade"),
            ("Sec-WebSocket-Accept", websocketKey)
        ])
        conn.sendall(response.encode())

    def generateKey(self, key):
        keyHash = hashlib.sha1((key + GUID).encode())
        keyEncode = base64.b64encode(keyHash.digest())
        return keyEncode.decode()
    
    def encode(self, content, opCode):
        header = bytearray()
        contentLength = len(content)
        
        if contentLength <= 125:
            header.append(fin | opCode)
            header.append(contentLength)
        elif 126 <= contentLength <= 65535:
            header.append(fin | opCode)
            header.append(len_16)
            header.extend(struct.pack(">H", contentLength))
        elif contentLength < 18446744073709551616:
            header.append(fin | opCode)
            header.append(len_64)
            header.extend(struct.pack(">Q", contentLength))
        else:
            return
        
        return header + content
    
    def decode(self, content):
        opCode = content[0] & opcode
        contentLength = content[1] & length

        if contentLength == 126:
            contentLength = struct.unpack(">H", content[3:5])[0]
            masks = content[6:10]
            contentRead = content[10:10 + contentLength]
        elif contentLength == 127:
            contentLength = struct.unpack(">Q", content[3:11])[0]
            masks = content[12:16]
            contentRead = content[16:16 + contentLength]
        else:
            masks = content[2:6]
            contentRead = content[6:6+contentLength]

        message = bytearray()
        for x in contentRead:
            x ^= masks[len(message) % 4]
            message.append(x)

        return message, opCode
    
    def send(self, content, opCode):
        self.conn.sendall(self.encode(content, opCode))

    def close(self):
        self.send("", opcode_close)
        self.conn.close()
    
    def run_forever(self):
        while True:
            try:
                message = self.conn.recv(config.socket_max_receive_size)
                content, opCode = self.decode(message)

                if opCode == opcode_text:
                    self.onmessage(self, content)
                elif opCode == opcode_close:
                    self.conn.close()
                    self.onclose(self)
                    break
                elif opCode == opcode_ping:
                    self.send(content, opcode_pong)

            except:
                self.conn.close()
                self.onclose()
                break

    def onmessage(self, message):
        pass

    def onclose(self):
        pass
