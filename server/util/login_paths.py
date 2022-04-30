from util.response import generate_response, redirect_response

from util.router import Route
import util.mongodb as db
import bcrypt
import random

def add_paths(router):
    router.add_route(Route("POST", "/registration-form", registration))
    router.add_route(Route("POST", "/login-form", login))
    router.add_route(Route("GET", "/logout", logout))


def registration(request, handler):
    """
    Add username, salted password, and user's auth_token in db    
    """
    encrypted_user_info = multipart_parser(request)
    encrypted_user_info["pwd"] = bcrypt.hashpw(bytes(encrypted_user_info["pwd"], 'utf-8'), bcrypt.gensalt())
    new_user = db.insert_new_user(encrypted_user_info)
    if new_user:
        response = generate_response(b"Registration successful, try logging in", "text/plain; charset=utf-8")
    else:
        response = generate_response(b"Username unavailable, try again", "text/plain; charset=utf-8", "404 Not Found")
    handler.request.sendall(response)


def login(request, handler):
    """
    Authenticate user by checking password
    Set the auth_token as a cookie, with HttpOnly directive, Max_Age=3600
    """
    user_info = multipart_parser(request)
    auth_token = random.randint(1, 1000000000)
    user_info["auth_token"] = auth_token    
    if db.auth_user(user_info):
        # response = generate_response(b"Login successful!", "text/plain; charset=utf-8", '200 OK', 
        #                             [("Set-Cookie", "auth_token="+str(auth_token)+";Max-Age=3700;HttpOnly")])
        # handler.request.sendall(response)
        response = redirect_response("/index", "302 Found", [("Set-Cookie", "auth_token="+str(auth_token)+";Max-Age=3700;HttpOnly")])
        handler.request.sendall(response)
        return
    response = generate_response(b"Error try again, password or email is incorrect!", "text/plain; charset=utf-8", '200 OK', 
                                    [("Set-Cookie", "auth_token="";expires=Thu, 01 Jan 1970 00:00:00 GMT;HttpOnly")])
    handler.request.sendall(response)


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
            

def logout(_, handler):
    response = redirect_response("/login", "302 Found", [("Set-Cookie", "auth_token="";expires=Thu, 01 Jan 1970 00:00:00 GMT;HttpOnly")])
    handler.request.sendall(response)


def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.split(b'\r\n')
    for line in lines_as_str:
        splits = line.split(b":")
        headers[splits[0].strip()] = splits[1].strip()
    return headers
