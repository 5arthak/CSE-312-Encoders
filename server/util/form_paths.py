# import form_parser as fp
import random
from util.response import redirect_response
from util.response import generate_response

from util.router import Route
import util.mongodb as db
from util.tokens import tokens
from util.security import secure_html


# from util.request import Request


def add_paths(router):
    router.add_route(Route("POST", "/image-upload", image_upload))


def image_upload(request, handler):
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]
    if not form_parser(request.body, boundary.encode()):
        response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
        handler.request.sendall(response)
        return
    response = redirect_response("/") 
    handler.request.sendall(response)

def form_parser(request, boundary):
    content = request.split(boundary)
    comment = {}
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1]
        if name == '"comment"':
            comment["comment"] = secure_html(body.decode())
        if name == '"upload"':
            comment["img_name"] = parse_image(body)
        if name == '"xsrf_token"':
            token = body.decode().split('\r\n')[0]
            if token not in tokens:
                return False
    db.insert_comment(comment)
    return True
            

def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.split(b'\r\n')
    for line in lines_as_str:
        splits = line.split(b":")
        headers[splits[0].strip()] = splits[1].strip()
    return headers
    

def parse_image(image_bytes):
    img_name = "image" + str(random.randint(1, 1000000)) + ".jpg"
    with open("public/image/" + img_name, "wb") as output_file:
        output_file.write(image_bytes)
    return img_name
  


# Hosting files - security
# remove all / characters 
# no GET /image/~.ssh/id_rsa

# Turn off MIME type sniffing