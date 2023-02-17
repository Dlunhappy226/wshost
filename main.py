import traceback
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
    scriptFound = False
    try:
        header = headers.decode(request)
        head = header[0].split(" ")
        head[1] = head[1].partition("?")[0]
        for key in config.custom_script:
            if "*" in key:
                if key.split("*")[0] in head[1]:
                    try:
                        config.custom_script[key]({"conn": conn, "addr": addr, "content": request})
                    except:
                        traceback.print_exc()
                        response = headers.encode("500 Internal Server Error", [
                            ("Content-Length", "173"),
                            ("Content-Type", "text/html")
                        ]).encode() + files.read(config.root_directory + "/500.html")
                        conn.sendall(response)
                    scriptFound = True
                    break
            elif key == head[1]:
                try:
                    config.custom_script[key]({"conn": conn, "addr": addr, "content": request})
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
            response = files.handleRequest(head)
    except:
        response = headers.encode("400 Bad Request", []).encode() + b"400 Bad Request"
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
