from wshost import clients
import threading
import socket
import time
import sys


class App:
    def __init__(self, config):
        if(config.startup):
            print("Starting WSHost")
        self.config = config

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((config.host, config.port))
        server.listen(512)

        address = server.getsockname()

        if(config.startup):
            print("WSHost listening {}:{}".format(address[0], address[1]))

        threading.Thread(target=self.main, args=(server,), daemon=True).start()

        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Exiting")
            server.close()
            sys.exit()


    def main(self, server):
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=clients.Clients(conn, addr, self.config).run_forever, daemon=True).start()
            except:
                return
