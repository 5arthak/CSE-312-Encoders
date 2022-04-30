from urllib import response
from util.router import Route
from util.response import generate_response, redirect_response
from util.security import secure_html
# from util.template_engine import render_template
import util.mongodb as db
import secrets


def add_paths(router):
    
    router.add_route(Route("GET", "/createList.html", show_list_submission))

    # JS, CSS, ICO stuff
    router.add_route(Route("GET", "/functions.js", js))
    router.add_route(Route("GET", "/style.css", style))
    router.add_route(Route("GET", "/favicon.ico", favicon))

    # Pages 
    router.add_route(Route("GET", "/login", login))
    router.add_route(Route("GET", "/register", register))
    router.add_route(Route("GET", "/index", index))
    router.add_route(Route("GET", "/createList", create_list))
    router.add_route(Route("GET", "/addReceipt", add_receipt))


    router.add_route(Route("GET", "/.", four_oh_four))
    router.add_route(Route("GET", "/", check_user_status))

    
def check_user_status(request, handler):
    # check if user is logged in if so direct to home page else direct them to login page.
    if is_log_in(request):
        response = redirect_response("/index", "302 Found")
    else:
        response = redirect_response("/login", "302 Found")
    # response = redirect_response("/index", "302 Found")
    handler.request.sendall(response)
    

def login(request, handler):
    send_file("public/login.html", "text/html", request, handler)

def register(request, handler):
    send_file("public/register.html", "text/html", request, handler)

def index(request, handler):
    send_file("public/index.html", "text/html", request, handler)

def create_list(request, handler):
    send_file("public/createList.html", "text/html", request, handler)

def add_receipt(request, handler):
    send_file("public/addReceipt.html", "text/html", request, handler)

def four_oh_four(_, handler):
    response = generate_response(b"The requested content does not exist", "text/plain; charset=utf-8", "404 Not Found")
    handler.request.sendall(response)



def favicon(request, handler):
    image_name = "public"+request.path
    send_file(str(image_name), "image/png", request, handler)

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


# Misc.
def is_log_in(request):
    _, user = get_cookies(request)
    if user == None:
        return False
    return True

def get_cookies(request):
    # Returns the cookies and username (aka email)
    cookies = None
    username = None
    cookie = request.headers.get("Cookie")
    if cookie != None:
        cookies = parse_cookie(cookie)
        if cookies.get("auth_token") != None:
            user = db.user_token(cookies["auth_token"])
            if len(user) != 0:
                username = secure_html(user[0].get("username"))
    return (cookies, username)
    

def parse_cookie(cookie):
    cookies = {}
    cookie = cookie.split(";")
    for c in cookie:
        try:
            cookies[c.split("=")[0].strip()] = c.split("=")[1].strip()
        except:
            cookies[c.strip()] = True
    return cookies