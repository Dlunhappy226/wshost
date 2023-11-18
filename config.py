#Socket binding address
host = ""
port = 8000

#Server config
socket_max_receive_size = 1000000

#File config
root_directory = "html"

#Routing

routing = {
}

#Error page

error_html = """<html>
<head><title>{}</title></head>
<body>
<center><h1>{}</h1></center>
<hr><center>WSHost/1.0</center>
</body>
</html>"""
