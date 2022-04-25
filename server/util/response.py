
def generate_response(body:bytes, content_type:str = 'text/plain; charset=utf-8', status:str = '200 OK', headers:list = []):
    response = ("HTTP/1.1 " + status + "\r\n").encode()
    if content_type != "NA":
        response += b'X-Content-Type-Options: nosnif\r\n'
        response += ("Content-Length: " + str(len(body)) + "\r\n").encode()
        response += ("Content-Type: " + content_type + "\r\n").encode()
    for head in headers:
        response += head
    response += b"\r\n" + body
    return response

def redirect_response(redirect: str, status: str = '301 Moved Permanently'):
    response = ("HTTP/1.1 " + status + "\r\n").encode()
    response += b'X-Content-Type-Options: nosniff\r\n'
    response += ("Location: " + redirect + "\r\n\r\n").encode()
    response += ("Content-Length: 0\r\n").encode()
    return response

    # response = b"HTTP/1.1 302 Found\r\nX-Content-Type-Options: nosnif\r\nLocation: /\r\nContent-Length: 0\r\n\r\n"

def Header(key, value):
    response = (key).encode() + b": " + value.encode() + b'\r\n'
    return response