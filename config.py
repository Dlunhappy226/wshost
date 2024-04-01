from route import route, error_route


#Socket binding address
host = "0.0.0.0"
port = 8000


#File config
root_directory = "html"
max_upload_size = 1024 * 1024
buffer_size = 8 * 1024


#Error page
error_html = """<html>
<head><title>{}</title></head>
<body>
<center><h1>{}</h1></center>
<hr><center>WSHost/1.0</center>
</body>
</html>
"""


#Message
startup = True
debug = True
