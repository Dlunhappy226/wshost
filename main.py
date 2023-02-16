import threading
import headers
import socket
import config

print("Starting WSHost")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((config.host, config.port))
server.listen()

def clientHandler(conn, addr):
    request = conn.recv(config.socket_max_receive_size)
    response = headers.encode("200 OK", [("Set-Cookie", "test1=test"), ("Set-Cookie", "test2=test")]) + "Hello World!"
    conn.sendall(response.encode())
    conn.close()

address = server.getsockname()

print("WSHost listening {}:{}".format(address[0], address[1]))

while True:
    conn, addr = server.accept()
    clientThread = threading.Thread(target=clientHandler, args=(conn, addr))
    clientThread.start()

server.close()
