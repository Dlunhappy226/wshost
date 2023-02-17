import headers

def test(event):
    event["conn"].sendall(headers.encode("200 OK", []).encode() + b"Hello World!")