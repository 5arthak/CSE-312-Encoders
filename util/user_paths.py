import json

import util.mongodb as db
from util.response import generate_response
from util.router import Route


def add_paths(router):
    router.add_route(Route('POST', '/users', create))
    router.add_route(Route('GET', '/users/.', retrieve))
    router.add_route(Route('GET', '/users', list_all))
    router.add_route(Route('PUT', '/users/.', update))
    router.add_route(Route('DELETE', '/users/.', delete))



def create(request, handler):
    if len(request.body) == 0:
        response = generate_response(b"Error: No content", "text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(response)
        return 
    body_string = request.body.decode()
    body_dict = json.loads(body_string)
    json_body = json.dumps(db.create(body_dict))
    json_byte = json_body.encode()
    response = generate_response(json_byte, 'application/json', "201 Created")
    handler.request.sendall(response)


def list_all(_, handler):
    user_list = db.list_all()
    response = generate_response(json.dumps(user_list).encode(), 'application/json')
    handler.request.sendall(response)
    

def retrieve(request, handler):
    prefix = "/users/"
    get_id = int(request.path[len(prefix):])
    id_data = db.retrieve(get_id)
    if len(id_data) == 0:
        response = generate_response(b"No user id", "text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(response)
        return
    response = generate_response(json.dumps(id_data).encode(), 'application/json')
    handler.request.sendall(response)
    


def update(request, handler):
    update_dict = json.loads(request.body.decode())
    prefix = "/users/"
    get_id = int(request.path[len(prefix):])
    update_email = update_dict.get("email")
    update_username = update_dict.get("username")
    if db.update(get_id, update_email, update_username):
        response = generate_response(json.dumps({"success":"true"}).encode(), 'application/json')
        handler.request.sendall(response)
    else:
        response = generate_response(json.dumps({"success": "false"}).encode(), 'application/json', "404 Not Found")
        handler.request.sendall(response)


def delete(request, handler):
    prefix = "/users/"
    get_id = int(request.path[len(prefix):])
    if db.delete(get_id):
        response = generate_response(b"", "text/plain; charset=utf-8", "204 No Content")
        handler.request.sendall(response)
    else:
        response = generate_response(b"Error: The requested content does not exist", "text/plain; charset=utf-8", "404 Not Found")
        handler.request.sendall(response)
