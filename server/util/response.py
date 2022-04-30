
def generate_response(body:bytes, content_type:str = 'text/plain; charset=utf-8', status:str = '200 OK', headers:list = []):
    response = ("HTTP/1.1 " + status + "\r\n").encode()
    if content_type != "NA":
        response += b'X-Content-Type-Options: nosnif\r\n'
        response += ("Content-Length: " + str(len(body)) + "\r\n").encode()
        response += ("Content-Type: " + content_type + "\r\n").encode()
    for header in headers:
        response += Header(header[0], header[1]) # Key: value\r\n
    response += b"\r\n" + body
    return response

def redirect_response(redirect, status:str = '302 Found', headers:list = []):
    # example redirect: b"HTTP/1.1 302 Found\r\nX-Content-Type-Options: nosnif\r\nLocation: /\r\nContent-Length: 0\r\n\r\n"
    response = ("HTTP/1.1 " + status + "\r\n").encode()
    response += b'X-Content-Type-Options: nosnif\r\n'
    for header in headers:
        response += Header(header[0], header[1]) # Key: value\r\n
    response += ("Location: " + redirect + "\r\n\r\n").encode()
    response += ("Content-Length: 0\r\n").encode()
    return response


def Header(key, value):
    response = str(key).encode() + b": " + str(value).encode() + b'\r\n'
    return response