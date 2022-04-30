import random
from util.response import redirect_response, generate_response

from util.router import Route
import util.mongodb as db
from util.security import secure_html

# from util.request import Request


def add_paths(router):
    # router.add_route(Route("POST", "/image-upload", image_upload))
    router.add_route(Route("POST", "/newList-upload", upload_list))


def upload_list(request, handler):
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]

    if not list_parser(request.body, boundary.encode()):
        response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
        handler.request.sendall(response)
        return
    response = redirect_response("/createList.html") 
    handler.request.sendall(response)



# def image_upload(request, handler):
#     content_type = request.headers.get('Content-Type')
#     prefix = 'multipart/form-data; boundary='
#     boundary = "--" + content_type[len(prefix):]
#     if not form_parser(request.body, boundary.encode()):
#         response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
#         handler.request.sendall(response)
#         return
#     response = redirect_response("/") 
#     handler.request.sendall(response)

def list_parser(request, boundary): # "item", "name", "quantity"
    content = request.split(boundary)
    grocery_list = {}
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1]
        if name == '"name"':
            grocery_list["name"] = secure_html(body.decode()).strip()
        elif name == '"item"':
            grocery_list["item"] = secure_html(body.decode()).strip()
        elif name == '"quantity"':
            grocery_list["quantity"] = secure_html(body.decode()).strip()
    list_name = grocery_list.get("name","")
    item_name = grocery_list.get("item","")
    quantity = grocery_list.get("quantity","0")
    db.add_item(list_name, item_name, quantity)
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