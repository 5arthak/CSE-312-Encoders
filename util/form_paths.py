import random
from util.response import redirect_response, generate_response

from util.router import Route
import util.mongodb as db
from util.security import secure_html
import json



def add_paths(router):
    
    # Form paths
    router.add_route(Route("POST", "/image-upload", image_upload))
    router.add_route(Route("POST", "/create-new-list", create_new_list))
    # Database path
    router.add_route(Route("GET", "/list-.", chat_history))
    router.add_route(Route("GET","/chat-.", get_chat_of))
    
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

# Parsing the request body for the new list name.
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
            list_name= list_name.replace(" ", "_")
            db.create_new_list(list_name)
    return True


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

# Parsing the request body for the image upload.
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


def chat_history(request, handler):
    history = [{"item-name": "peanut", "quantity": 1}, 
               {"item-name": "walnut", "quantity": 3}]
    prefix = "/list-"
    get_list_name = str(request.path[len(prefix):])
    history = db.retrieve_items(get_list_name)
    response = generate_response(json.dumps(history).encode(), "application/json; charset=utf-8", "200 OK")
    handler.request.sendall(response)


def get_chat_of(request, handler):
    prefix = "/chat-"
    get_username = str(request.path[len(prefix): ])
    user_chats = db.get_user_messages(get_username)

    print("users:", get_username, user_chats[0], flush=True)

    response = generate_response(json.dumps(user_chats[0]).encode(), "application/json; charset=utf-8", "200 OK")
    handler.request.sendall(response)

            

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