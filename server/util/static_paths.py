from urllib import response
from util.router import Route
from util.response import generate_response, redirect_response
from util.template_engine import render_template
import util.mongodb as db
import secrets
from util.tokens import tokens


def add_paths(router):
    
    router.add_route(Route("GET", "/createList.html", show_list_submission))

    router.add_route(Route("GET", "/functions.js", js))
    router.add_route(Route("GET", "/style.css", style))

    router.add_route(Route("GET", "/favicon.ico", favicon))
    router.add_route(Route("GET", "/index.html", redir_home))

    router.add_route(Route("GET", "/hello", hello))

    router.add_route(Route("GET", "/.", four_oh_four))

    router.add_route(Route("GET", "/", home))

    

def four_oh_four(request, handler):
    response = generate_response(b"The requested content does not exist", "text/plain; charset=utf-8", "404 Not Found")
    handler.request.sendall(response)


def hello(request, handler):
    response = generate_response("Hello World!".encode())
    handler.request.sendall(response)


def redir_home(request, handler):
    response = redirect_response("/", "301 Moved Permanently")
    handler.request.sendall(response)

def favicon(request, handler):
    image_name = "public"+request.path
    send_file(str(image_name), "image/png", request, handler)

def home(request, handler):
    send_file("public/index.html", "text/html", request, handler)


def js(request, handler):
    send_file("public/functions.js", "text/javascript; charset=utf-8", request, handler)


def style(request, handler):
    send_file("public/style.css", "text/css; charset=utf-8", request, handler)

def show_list_submission(request,handler):
    send_file("public/createList.html", "text/html", request, handler)

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

