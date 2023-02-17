import threading
import headers
import socket
import config
import files

print("Starting WSHost")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((config.host, config.port))
server.listen()

def clientHandler(conn, addr):
    request = conn.recv(config.socket_max_receive_size)
    try:
        header = headers.decode(request)
        head = header[0].split(" ")
        response = files.handleRequest(head)
    except:
        response = headers.encode("400 Bad Request", []).encode() + "400 Bad Request".encode()
    conn.sendall(response)
    conn.close()

address = server.getsockname()

print("WSHost listening {}:{}".format(address[0], address[1]))

while True:
    conn, addr = server.accept()
    clientThread = threading.Thread(target=clientHandler, args=(conn, addr))
    clientThread.start()

server.close()
