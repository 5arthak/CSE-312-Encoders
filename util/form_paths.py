import random
from util.response import redirect_response, generate_response

from util.router import Route
import util.mongodb as db
from util.security import secure_html

# from util.request import Request


def add_paths(router):
    router.add_route(Route("POST", "/image-upload", image_upload))
    router.add_route(Route("POST", "/newList-upload", upload_list))
    router.add_route(Route("POST", "/create-new-list", create_new_list))

    
# Parser for creating new grocery list
def create_new_list(request, handler):
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]
    if not new_list_parser(request.body, boundary.encode()):
        response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
        handler.request.sendall(response)
        return
    response = redirect_response("/index") 
    handler.request.sendall(response)

def new_list_parser(request, boundary):
    content = request.split(boundary)
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1].split(b'\r\n')[0]
        if name == '"new_list_name"':
            list_name = body.decode()
            list_name = secure_html(list_name)
            
            print("list_name", list_name)
            db.insert_new_list(list_name)
            # create_list_page(list_name)
    return True

# def create_list_page(list_name):
#     new_list_page = "public/list/" + list_name
#     with open(new_list_page, "w") as output_file:
#         template_html = open("ceateList.html", "r")
#         output_file.write(template_html.read())
#     return

# Parser for Image upload on the deals page
def image_upload(request, handler):
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]
    if not image_parser(request.body, boundary.encode()):
        response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
        handler.request.sendall(response)
        return
    response = redirect_response("/addDeals") 
    handler.request.sendall(response)

def image_parser(request, boundary):
    content = request.split(boundary)
    comment = {}
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1].split(b'\r\n')[0]
        if name == '"comment"':
            comment["comment"] = secure_html(body.decode())
        if name == '"upload"':
            comment["img_name"] = parse_image(body)
    db.insert_deal(comment)
    return True


# Parser for uploading list 
def upload_list(request, handler):
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]

    if not list_parser(request.body, boundary.encode()):
        response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
        handler.request.sendall(response)
        return
    response = redirect_response("/createList") 
    handler.request.sendall(response)


def list_parser(request, boundary): # "item", "name", "quantity"
    content = request.split(boundary)
    grocery_list = {}
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1]
        if name == '"item"':
            grocery_list["item_name"] = secure_html(body.decode()).strip()
        elif name == 'item_upload':
            grocery_list["item_image"] = parse_image(body)
        elif name == '"quantity"':
            grocery_list["quantity"] = secure_html(body.decode()).strip()
    item_name = grocery_list.get("item_name","")
    item_image = grocery_list.get("item_image","")
    quantity = grocery_list.get("quantity","0")

    item_filename = "public/" + "{{list_name}}" + "_" + item_name + ".jpg"
    with open(item_filename, 'wb') as image_file:


        pass
    db.add_item(item_image, item_name, quantity)
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