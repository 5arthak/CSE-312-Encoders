from urllib import response
from util.router import Route
from util.response import generate_response
from util.template_engine import render_template
import util.mongodb as db
import secrets
from util.tokens import tokens


def add_paths(router):
    router.add_route(Route("GET", "/functions.js", js))
    router.add_route(Route("GET", "/style.css", style))
    router.add_route(Route("GET", "/image/.", images))
    # router.add_route(Route("POST", "/register", "registration"))
    router.add_route(Route("GET", "/favicon.ico", favicon))
    router.add_route(Route("GET", "/hi", hi))
    router.add_route(Route("GET", "/hello", hello))
    router.add_route(Route("GET", "/.", four_oh_four))
    router.add_route(Route("GET", "/", home))

def four_oh_four(_, handler):
    response = generate_response(b"The requested content does not exist", "text/plain; charset=utf-8", "404 Not Found")
    handler.request.sendall(response)


def hello(_, handler):
    response = generate_response("Hello World!".encode())
    handler.request.sendall(response)


def hi(_, handler):
    response = b"HTTP/1.1 301 Moved Permanetly\r\nX-Content-Type-Options: nosnif\r\nLocation: /hello\r\nContent-Length: 0\r\n\r\n"
    handler.request.sendall(response)

def favicon(request, handler):
    image_name = "public"+request.path
    send_file(str(image_name), "image/png", request, handler)

def home(_, handler):
    # Edit this to test locally
    comments = [{"comment": "Nice Duck", "img_name": "duck.jpg"}, {"comment": "<b>Homie</b>", "img_name": "dog.jpg"}]
    comments = db.list_all_comments() 
    token = str(secrets.token_urlsafe(16))
    tokens.append(token)
    content = render_template("public/index.html", {
        "image_name": "Duck",
        "image_filename": "duck.jpg",
        "token": token,
        "loop_data": comments})
    
    response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(response)


def js(request, handler):
    send_file("public/functions.js", "text/javascript; charset=utf-8", request, handler)


def style(request, handler):
    send_file("public/style.css", "text/css; charset=utf-8", request, handler)


def images(request, handler):
    path_prefix = '/image/'
    image_name = request.path[request.path.find(path_prefix) + len(path_prefix):]
    image_name = image_name.replace("/", "") #Security measurement
    send_file("public/image/" + str(image_name), "image/jpeg", request, handler)


def send_file(filename, mime_type, request, handler):
    try:
        with open(filename, "rb") as content:
            body = content.read()
            response = generate_response(body, mime_type, "200 OK")
            handler.request.sendall(response)
    except:
        response = generate_response(b"The requested content does not exist", "text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(response)


# def registration(request, handler):
#     print(request.body)
#     response = generate_response("It worked!!".encode(), "text/plain; charset=utf-8")
#     handler.request.sendall(response)