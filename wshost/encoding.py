def read_chunked(request):
    def read(buffer, body):
        read_data = b""
        for x in range(buffer):
            if body != b"":
                read_data += body[:1]
                body = body[1:]

            else:
                read_data += request["conn"].recv(1)
                
        return read_data, body
    
    data = b""
    body = request["body"]

    while True:
        chunk_size_str = b""
        while True:
            char, body = read(1, body)
            if char == b"\r":
                char, body = read(1, body)
                break

            chunk_size_str += char

        chunk_size = int(chunk_size_str, 16)
        if (len(body) + chunk_size) > request["config"].max_upload_size:
            return False
        
        if chunk_size == 0:
            char, body = read(2, body)
            break
        
        char, body = read(chunk_size, body)
        data += char
        char, body = read(2, body)

    return data
