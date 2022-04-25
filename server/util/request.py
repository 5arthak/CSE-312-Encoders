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



def _parse_submission(request: Request):
    print("parsing",flush=True)
    body = request.allparsed()["_BODY"]

    boundary = request.allparsed()["Content-Type"].split("boundary=")[1].encode()

    parts = {}

    startboundary = b'--' + boundary
    endboundary = startboundary + b'--'

    multiparts = body.split(startboundary)

    #print("multipart len", len(multiparts),flush=True)

    # checked if multipart len > 0
    for part in multiparts:
        #print("part", part,flush=True)
        if part == b'' : continue
        if part[0:2] == b'--': break #signifies end of multipart
        
        startofheaders = part.find(b'\r\n')
        startofbody = part.find(b'\r\n\r\n')

        headers = part[startofheaders : startofbody].decode()
        content = part[startofbody+4 : -2] # -2 removes \r\n

        header = headers.split("\r\n")
        currheaders = {}

        for h in header:
            if h == "": continue

            head = h.split(":")

            currheaders[str(head[0])] = head[1].strip()
        
        # CHANGE THIS
        dispositioninfo = currheaders["Content-Disposition"]
        dispositioninfo = dispositioninfo.split(";",1)[1]

        startofname = dispositioninfo.find("name=")
        endofname = dispositioninfo.find(";")
        name = dispositioninfo[startofname+5 : endofname].replace('\"',"")
        rest = dispositioninfo[endofname+1 : ]


        infoheaders = {}

        inforest = rest.split(";")
        for iheader in inforest:
            identifiers = iheader.split("=")

            ihkey = str(identifiers[0].strip())
            ihvalue = identifiers[1].replace("\"","")

            if ihvalue == name: continue

            infoheaders[ihkey] = ihvalue

        parts[name] = {}
        parts[name]["headers"] = infoheaders 
        parts[name]["content"] = content

        
        #print("content",content,flush=True)
        #print("parts adding", parts, flush=True)

    print()
    #print("parts" ,parts,flush=True)
    print()

    return parts
