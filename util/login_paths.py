from util.response import generate_response, redirect_response
from util.router import Route
import util.mongodb as db
import bcrypt
import random
from util.security import secure_html
import re

def add_paths(router):
    router.add_route(Route("POST", "/registration-form", registration))
    router.add_route(Route("POST", "/login-form", login))
    router.add_route(Route("GET", "/logout", logout))
    router.add_route(Route("POST", "/pronouns", update_pronouns))

def registration(request, handler):
    """
    Add username, salted password, and user's auth_token in db
    """
    encrypted_user_info = multipart_parser(request)
    if(password_strength(encrypted_user_info["pwd"])):
        print("in here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        encrypted_user_info["pwd"] = bcrypt.hashpw(bytes(encrypted_user_info["pwd"], 'utf-8'), bcrypt.gensalt())
        encrypted_user_info["pronouns"] = ''
        new_user = db.insert_new_user(encrypted_user_info)
        if new_user:
            response = redirect_response("/login")
        else:
            response = generate_response(b"Username unavailable, try again", "text/plain; charset=utf-8", "404 Not Found",
                                    [("Set-Cookie", "auth_token="";expires=Thu, 01 Jan 1970 00:00:00 GMT;HttpOnly")])

        handler.request.sendall(response)
    else:
        response = generate_response(b"You have entered an invalid password. Please create a stronger password.", "text/plain; charset=utf-8", "400 Bad request",
                                    [("Set-Cookie", "auth_token="";expires=Thu, 01 Jan 1970 00:00:00 GMT;HttpOnly")])
        handler.request.sendall(response)


def login(request, handler):
    """
    Authenticate user by checking password
    Set the auth_token as a cookie, with HttpOnly directive, Max_Age=3600
    """
    user_info = multipart_parser(request)
    auth_token = random.randint(1, 1000000000)
    user_info["auth_token"] = auth_token    
    # MyTCPHandler.ws_connections[user_info['email']] = handler
    if db.auth_user_login(user_info):
        response = redirect_response("/index", "302 Found", [("Set-Cookie", "auth_token="+str(auth_token)+";Max-Age=3700;HttpOnly")])
        handler.request.sendall(response)
        return
    response = generate_response(b"Error try again, password or email is incorrect!", "text/plain; charset=utf-8", '200 OK', 
                                    [("Set-Cookie", "auth_token="";expires=Thu, 01 Jan 1970 00:00:00 GMT;HttpOnly")])
    
    handler.request.sendall(response)


def logout(request, handler):
    _, email = get_cookies(request)
    db.user_logoff(email)
    response = redirect_response("/login", "302 Found", [("Set-Cookie", "auth_token="";expires=Thu, 01 Jan 1970 00:00:00 GMT;HttpOnly")])
    handler.request.sendall(response)



# Update pronouns for persistant setting criteria
def update_pronouns(request, handler):
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]
    if not form_parser(request, boundary.encode()):
        response = generate_response(b"Requested rejected", "text/plain; charset=utf-8", "403 Forbidden")
        handler.request.sendall(response)
        return
    response = redirect_response("/onlineUsers") 
    handler.request.sendall(response)

def form_parser(request, boundary):
    content = request.body.split(boundary)
    comment = {}
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1].split(b'\r\n')[0]
        if name == '"pronouns"':
            comment["pronouns"] = secure_html(body.decode())
    _, email = get_cookies(request)
    db.update_pronouns(email, comment["pronouns"])
    return True



def multipart_parser(request):
    """
    outputs user_info = {"email" : "email", 
                        "pwd" : "pwd"
                        }
    """
    content_type = request.headers.get('Content-Type')
    prefix = 'multipart/form-data; boundary='
    boundary = "--" + content_type[len(prefix):]
    boundary = boundary.encode()
    content = (request.body).split(boundary)
    user_info = {}
    for x in range(1, len(content)-1):
        raw_header = (content[x][2:]).split(b'\r\n\r\n')
        header = (parse_headers(raw_header[0]))
        name = header[b'Content-Disposition'].split(b';')[1].split(b'=')[1].decode()
        body = raw_header[1].split(b'\r\n')[0]
        if name == '"email"':
            user_info["email"] = body.decode()
        if name == '"pwd"':
            user_info["pwd"] = body.decode()
    return user_info
            



def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.split(b'\r\n')
    for line in lines_as_str:
        splits = line.split(b":")
        headers[splits[0].strip()] = splits[1].strip()
    return headers

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

    

def password_strength(pwd):
    if(len(pwd)>=8):
        if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',pwd))==True):
            print("The password is strong")
            return True
        elif(bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})',pwd))==True):
            print("The password is weak")
            return False
    else:
        print("You have entered an invalid password.")
        return False