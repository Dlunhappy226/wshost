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
                    errorMessage = config.error_html.format("500 Internal Server Error", "500 Internal Server Error").encode()
                    response = headers.encode("500 Internal Server Error", [
                        ("Content-Length", len(errorMessage)),
                        ("Content-Type", "text/html")
                    ]).encode() + errorMessage
                    conn.sendall(response)
                scriptFound = True
                break
        if not scriptFound:
            try:
                response = files.handleRequest(head, config.root_directory, config.error_html)
            except:
                traceback.print_exc()
                errorMessage = config.error_html.format("500 Internal Server Error", "500 Internal Server Error").encode()
                response = headers.encode("500 Internal Server Error", [
                    ("Content-Length", len(errorMessage)),
                    ("Content-Type", "text/html")
                ]).encode() + errorMessage
                conn.sendall(response)
    except:
        errorMessage = config.error_html.format("400 Bad Request", "400 Bad Request").encode()
        response = headers.encode("400 Bad Request", [
            ("Content-Length", len(errorMessage)),
            ("Content-Type", "text/html")
        ]).encode() + errorMessage
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
