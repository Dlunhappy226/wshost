#Socket binding address
host = ""
port = 8000

#Server config
socket_max_receive_size = 4096

#File config
root_directory = "html"

#Custom script

import test

routing = {
    "/test": test.test
}
