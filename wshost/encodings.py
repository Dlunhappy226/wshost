from wshost import exceptions


def read_chunked(request):
    def read(buffer):
        data_read = bytes()
        for x in range(buffer):
            data_read += request["conn"].recv(1)
                
        return data_read
    
    data = bytes()

    while True:
        chunk_size_str = bytes()
        while True:
            char = read(1)
            if char == b"\r":
                char = read(1)
                break

            chunk_size_str += char

        chunk_size = int(chunk_size_str, 16)
        if (len(data) + chunk_size) > request["config"].max_upload_size:
            raise exceptions.OverBuffer
        
        if chunk_size == 0:
            char = read(2)
            break
        
        char = read(chunk_size)
        data += char
        char = read(2)

    return data
