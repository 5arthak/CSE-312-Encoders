class Request():
    new_line = b'\r\n'
    blank_line_boundary = b'\r\n\r\n'

    def __init__(self, request:bytes):
        [request_line, self.headers_as_bytes, self.body] = split_request(request)
        [self.method, self.path, self.http_version] = parse_request(request)
        self.headers = parse_headers(self.headers_as_bytes)

def split_request(request: bytes):
    first_newline_boundary = request.find(Request.new_line)
    blank_line_boundary = request.find(Request.blank_line_boundary)

    request_line = request[:first_newline_boundary]
    header_as_bytes = request[(first_newline_boundary + len(Request.new_line)):blank_line_boundary]
    body = request[(blank_line_boundary + len(Request.blank_line_boundary)):]
    return [request_line, header_as_bytes, body]

def parse_request(request_line:bytes):  #LOOK AT THISSS
    parse = request_line.split(b' ')
    return [parse[0].decode(), parse[1].decode(), parse[2].decode()]

def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.decode().split(Request.new_line.decode())
    for line in lines_as_str:
        splits = line.split(":")
        headers[splits[0].strip()] = splits[1].strip()
    return headers

# Test
if __name__ == '__main__':
    sample = b'GET / HTTP/1.1\r\nHost:localhost:8080\r\n\r\nhello'
    request = Request(sample)
    pass