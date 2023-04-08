from wshost import headers
from wshost import files
import traceback
import threading
import fnmatch
import socket
import config

print("Starting WSHost")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
server.bind((config.host, config.port))
server.listen(1)

def clientHandler(conn, addr):
    request = conn.recv(config.socket_max_receive_size)
    scriptFound = False
    try:
        header = headers.decode(request)
        head = header[0].split(" ")
        head[1] = head[1].partition("?")[0]
        for key in config.routing:
            if fnmatch.fnmatch(head[1], key):
                try:
                    config.routing[key]({"conn": conn, "addr": addr, "content": request})
                except:
                    traceback.print_exc()
                    response = headers.encode("500 Internal Server Error", [
                        ("Content-Length", "173"),
                        ("Content-Type", "text/html")
                    ]).encode() + files.read(config.root_directory + "/500.html")
                    conn.sendall(response)
                scriptFound = True
                break
        if not scriptFound:
            response = files.handleRequest(head, config.root_directory)
    except:
        response = headers.encode("400 Bad Request", [
            ("Content-Length", "155"),
            ("Content-Type", "text/html")
        ]).encode() + files.read(config.root_directory + "/400.html")
    if not scriptFound:
        conn.sendall(response)
    conn.close()

address = server.getsockname()

print("WSHost listening {}:{}".format(address[0], address[1]))

while True:
    conn, addr = server.accept()
    clientThread = threading.Thread(target=clientHandler, args=(conn, addr))
    clientThread.start()

server.close()
