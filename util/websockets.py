from ast import parse
import hashlib
import codecs
import json
import random
import base64

from util.response import generate_response
from server import MyTCPHandler
# from util.request import Request
from util.router import Route
from util.security import secure_html
import util.mongodb as db
import sys


def add_paths(router):
    router.add_route(Route("GET", "/websocket", websocket))
    router.add_route(Route("GET", "/list-.", chat_history))


def websocket(request, handler):
    assert request.headers.get('Upgrade') == "websocket"

    websocket_key = request.headers.get('Sec-WebSocket-Key')
    accept = compute_accept(websocket_key)
    test_accept()
    response = generate_response(b'', "NA", "101 Switching Protocols", 
                                [("Sec-WebSocket-Accept", accept), ("Connection", "Upgrade"), ("Upgrade", "websocket")])

    handler.request.sendall(response)
    username = get_auth_token(request)
    MyTCPHandler.ws_connections[username] = handler
    while True:
        ws_frame_raw = handler.request.recv(1024)
        try:
            if ws_frame_raw[0] != b'':
                opcode = ws_frame_raw[0]
                if opcode == 136: 
                    del MyTCPHandler.ws_connections[username]
                    break
                elif opcode == 129: 
                    ws_length = ws_frame_raw[1]
                    masking_index = -1
                    if ws_length == 255: #64 bits
                        ws_length_bin = to_bin(ws_frame_raw[2]) + to_bin(ws_frame_raw[3]) + to_bin(ws_frame_raw[4]) + to_bin(ws_frame_raw[5]) + to_bin(ws_frame_raw[6]) + to_bin(ws_frame_raw[7]) + to_bin(ws_frame_raw[8]) + to_bin(ws_frame_raw[9])
                        ws_length = int(str(ws_length_bin), 2)
                        masking_index = 10
                        
                    elif ws_length == 254: #16 bits
                        ws_length_bin = to_bin(ws_frame_raw[2]) + to_bin(ws_frame_raw[3])
                        ws_length = int(str(ws_length_bin), 2)
                        masking_index = 4
                        
                    else: #7 bits
                        ws_length = ws_length & 127
                        masking_index = 2
                    mask = [ws_frame_raw[masking_index], ws_frame_raw[masking_index+1], ws_frame_raw[masking_index+2], ws_frame_raw[masking_index+3]]
                    payload = ws_frame_raw[masking_index+4:]
                    
                    while ws_length > len(payload):
                        more_ws_frame_raw = handler.request.recv(1024)
                        payload += more_ws_frame_raw[:]
                    
                    payload_decoded = ''
                    image_data = ''
                    for i in range(0, ws_length):
                        frame = payload[i]
                        unmasked = (mask[i % 4] ^ frame)
                        char = chr(unmasked)
                        payload_decoded += char
                        if 'image_data":' in str(payload_decoded):
                            image_data += char
                    image_data = base64.b64decode(image_data)
                    payload_decoded = json.loads(payload_decoded)
                    msg_type = payload_decoded["messageType"]
                    img_name = parse_image(image_data)                        
                    print(img_name)
                    if msg_type == "addItem":
                        # print(payload_decoded)
                        sys.stdout.flush()
                        sys.stderr.flush()
                        payload_decoded['item-name'] = secure_html(payload_decoded['item-name'])
                        outgoing_payload = json.dumps(payload_decoded)
                        outgoing_payload_len = len(outgoing_payload)
                        payload_decoded.pop('messageType')
                        payload_decoded.pop('image_data')
                        list_name = payload_decoded.pop('list_name')
                        # item = dict with item name and quanityt amt
                        db.insert_grocery_item(list_name, item=payload_decoded)
                        print(list_name, payload_decoded, flush = True)
                        outgoing_bytes = [129]
                        if outgoing_payload_len < 126:
                            outgoing_bytes.append(outgoing_payload_len)
                        elif outgoing_payload_len >=126 and outgoing_payload_len < 65536:
                            outgoing_bytes.append(126)
                            bin = str(to_bin(outgoing_payload_len))
                            ins = bin_to_int(bin, 2)
                            for x in ins:
                                outgoing_bytes.append(x)
                        else:
                            outgoing_bytes.append(127)
                            bin = str(to_bin(outgoing_payload_len))
                            ins = bin_to_int(bin, 8)
                            for x in ins:
                                outgoing_bytes.append(x)
                        for char in outgoing_payload:
                            utf = ord(char)
                            outgoing_bytes.append(utf)
                        outgoing_encoded = bytes(outgoing_bytes)
                        for tcp in MyTCPHandler.ws_connections.values():
                            tcp.request.sendall(outgoing_encoded)
                            
        except:
            pass

def parse_image(image_bytes):
    img_name = "list" + str(random.randint(1, 1000000)) + ".jpg"
    with open("public/image/" + img_name, "wb") as output_file:
        output_file.write(image_bytes)
    return img_name


def get_auth_token(request):
    cookie = request.headers.get("Cookie")
    if cookie != None:
        cookies = {}
        cookie = cookie.split(";")
        for c in cookie:
            try:
                cookies[c.split("=")[0].strip()] = c.split("=")[1].strip()
            except:
                cookies[c.strip()] = True
        return cookies.get('auth_token')
    

    
def to_bin(dec):
    binary = bin(dec).replace("0b", "") 
    while 8-len(binary)%8 < 8:
      binary = "0" + binary
    return binary
    
def bin_to_int(bin, bytes):
    ints = []
    for x in range(8, len(bin)+1, 8):
    #   print(x)
      ints.append(int(bin[x-8:x], 2))
    while len(ints) != bytes:
      ints.insert(0, 0)
    return ints


def compute_accept(websocket_key):
    websocket_key += "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    websocket_key = websocket_key.encode()
    hash_obj = hashlib.sha1(websocket_key)
    hexa_value = hash_obj.hexdigest()
    accept = codecs.encode(codecs.decode(hexa_value, 'hex'), 'base64').decode()
    return accept.strip()

def test_accept():
    test = "zKyj5z76FHrJjKkDLJ/6Hg=="
    output = "GYVPzWpCxGj2RfAb61I+7t4Yn6k="
    accept = compute_accept(test)
    assert accept == output, "testing accept"

def chat_history(request, handler):
    print(request.path, flush=True)
    history = [{"item-name": "peanut", "quantity": 1}, 
               {"item-name": "walnut", "quantity": 3}]
    prefix = "/list-"
    get_list_name = str(request.path[len(prefix):])
    print("get_list_name", get_list_name, flush=True)
    history = db.retrieve_items(get_list_name)
    print(history, flush=True)
    response = generate_response(json.dumps(history).encode(), "application/json; charset=utf-8", "200 OK")
    handler.request.sendall(response)