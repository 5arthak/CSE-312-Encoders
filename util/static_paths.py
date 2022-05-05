from queue import Empty
from urllib import response
from util.router import Route
from util.response import generate_response, redirect_response
from util.security import secure_html
from util.template_engine import render_template
import util.mongodb as db
import sys


def add_paths(router):    
    # JS, CSS, ICO stuff
    router.add_route(Route("GET", "/image/.", images))
    router.add_route(Route("GET", "/functions.js", js))
    router.add_route(Route("GET", "/style.css", style))
    router.add_route(Route("GET", "/favicon.ico", favicon))

    # Pages 
    router.add_route(Route("GET", "/login", login))
    router.add_route(Route("GET", "/register", register))
    router.add_route(Route("GET", "/index", index))
    # router.add_route(Route("GET", "/createList", create_list))
    router.add_route(Route("GET", "/addDeals", add_deals))
    router.add_route(Route("GET", "/onlineUsers", online_users))
    router.add_route(Route("GET", "/list.", render_list))


    router.add_route(Route("GET", "/.", four_oh_four))
    router.add_route(Route("GET", "/", check_user_status))

    
def check_user_status(request, handler):
    """
    check if user is logged in if so direct to home page else direct them to login page
    """
    if log_in(request):
        response = redirect_response("/index", "302 Found")
    else:
        response = redirect_response("/login", "302 Found")
    handler.request.sendall(response)
    

def login(request, handler):
    send_file("public/login.html", "text/html", request, handler)

def register(request, handler):
    send_file("public/register.html", "text/html", request, handler)

def index(request, handler):
    if not log_in(request):
        response = redirect_response("/login", "302 Found")
        handler.request.sendall(response)
        return
    get_list_names = db.get_list_names()
    content = render_template("public/index.html", {
        "loop_data": get_list_names})
    response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(response)

# def create_list(request, handler):
#     if not log_in(request):
#         response = redirect_response("/login", "302 Found")
#         handler.request.sendall(response)
#         return
#     list_items = db.list_grocery_items()
#     if(list_items):
#         for n in list_items:
#             content = render_template("public/createList.html", {
#                 "loop_data": n["items"]})
#         response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
#         handler.request.sendall(response)
#     else:
#         list_item = [{'list_name': '', 'items': [{'item_name': '', 'quantity': ''}]}]
#         for n in list_item:
#             content = render_template("public/createList.html", {
#                 "loop_data": n["items"]})
#         #print(get_list_items, "content", flush=True)
#         response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
#         handler.request.sendall(response)
#         send_file("public/createList.html", "text/html", request, handler)
        
def render_list(request, handler):
    # Check if user is logged in
    if not log_in(request):
        response = redirect_response("/login", "302 Found")
        handler.request.sendall(response)
        return
    # Then check if the path exist in db
    path_prefix = '/list'
    list_name = request.path[request.path.find(path_prefix) + len(path_prefix):]
    list_name = list_name.replace("/", "") #Security measurement
    # list_name = secure_html(list_name)
    print(list_name)
    print(db.not_a_list(list_name))
    if db.not_a_list(list_name):
        response = redirect_response("/index", "302 Found")
        handler.request.sendall(response)
        return 
    content = render_template("public/createList.html", {
        "list_name": list_name, 
        "loop_data": []})
    response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(response)


def add_deals(request, handler):
    if not log_in(request):
        response = redirect_response("/login", "302 Found")
        handler.request.sendall(response)
        return
    deals = db.list_all_deals() 
    print("deals", deals)
    content = render_template("public/addDeals.html", {
        "loop_data": deals})
    response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(response)

def online_users(request, handler):
    if not log_in(request):
        response = redirect_response("/login", "302 Found")
        handler.request.sendall(response)
        return
    online_users_list = db.get_online_users()
    _, email = get_cookies(request)
    user = next((i for i, item in enumerate(online_users_list) if item["email"] == email), None)
    pros = online_users_list[user].get("pronouns")
    online_users_list.pop(user)
    content = render_template("public/onlineUsers.html", {
        "user_email": email,
        "your_pronouns": pros,
        "loop_data": online_users_list})
    response = generate_response(content.encode(), "text/html; charset=utf-8", "200 OK")
    handler.request.sendall(response)




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


# Cookie Misc.
def log_in(request):
    _, user = get_cookies(request)
    if user == None:
        return False
    return True

def get_cookies(request):
    # Returns the cookies and email (aka usernam)
    cookies = None
    email = None
    cookie = request.headers.get("Cookie")
    if cookie != None:
        cookies = parse_cookie(cookie)
        if cookies.get("auth_token") != None:
            user = db.user_token(cookies["auth_token"])
            if len(user) != 0:
                email = secure_html(user[0].get("email"))
    return (cookies, email)

def parse_cookie(cookie):
    cookies = {}
    cookie = cookie.split(";")
    for c in cookie:
        try:
            cookies[c.split("=")[0].strip()] = c.split("=")[1].strip()
        except:
            cookies[c.strip()] = True
    return cookies