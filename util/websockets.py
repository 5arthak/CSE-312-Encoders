import hashlib
import codecs
import json
import random

from util.response import generate_response, Header
from server import MyTCPHandler
# from util.request import Request
from util.router import Route
from util.security import secure_html
import util.mongodb as db


def add_paths(router):
    router.add_route(Route("GET", "/websocket", websocket))
    router.add_route(Route("GET", "/chat-history", chat_history))


def websocket(request, handler):
    assert request.headers.get('Upgrade') == "websocket"

    websocket_key = request.headers.get('Sec-WebSocket-Key')
    accept = compute_accept(websocket_key)
    test_accept()
    accept_header = Header("Sec-WebSocket-Accept", accept)
    response = generate_response(b'', "NA", "101 Switching Protocols", 
                                [accept_header, Header("Connection", "Upgrade"), Header("Upgrade", "websocket")])
    handler.request.sendall(response)
    username = "User" + str(random.randint(0, 10000))
    MyTCPHandler.ws_connections[username] = handler
    MyTCPHandler.ws_conn_list.append(handler)
    other_index = 0
    if MyTCPHandler.ws_other.get(0) == None:
        MyTCPHandler.ws_other[0] = handler
        other_index = 1
    elif MyTCPHandler.ws_other.get(1) == None:
        MyTCPHandler.ws_other[1] = handler
        other_index = 0
    while True:
        ws_frame_raw = handler.request.recv(1024)
        try:
            if ws_frame_raw[0] != b'':
                opcode = ws_frame_raw[0]
                if opcode == 136: 
                    del MyTCPHandler.ws_connections[username]
                    break
                elif opcode == 129: 
                # send frames as needed (broadcast to all connection if its a chat msg or send to the other connection for webrtc)
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
                    for i in range(0, ws_length):
                        frame = payload[i]
                        char = chr(mask[i % 4] ^ frame)
                        payload_decoded += char
                    payload_decoded = json.loads(payload_decoded)
                    msg_type = payload_decoded["messageType"]
                    if msg_type == "chatMessage":
                        payload_decoded['comment'] = secure_html(payload_decoded['comment'])
                        payload_decoded['username'] = username
                        outgoing_payload = json.dumps(payload_decoded)
                        outgoing_payload_len = len(outgoing_payload)
                        payload_decoded.pop('messageType')
                        # db.insert_chat(payload_decoded)

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
                        for tcp in MyTCPHandler.ws_conn_list:
                            tcp.request.sendall(outgoing_encoded)
                    elif msg_type == "webRTC-offer" or "webRTC-answer" or "webRTC-candidate":
                        outgoing_bytes = []
                        for x in range(masking_index):
                            if x == 1:
                                outgoing_bytes.append(ws_frame_raw[x] & 127)
                            else:
                                outgoing_bytes.append(ws_frame_raw[x])
                        for i in range(0, ws_length):
                            frame = payload[i]
                            outgoing_bytes.append(mask[i % 4] ^ frame)

                        outgoing_encoded = bytes(outgoing_bytes)

                        other_tcp = MyTCPHandler.ws_other[other_index]
                        other_tcp.request.sendall(outgoing_encoded)
        except:
            pass
    

    
def to_bin(dec):
    binary = bin(dec).replace("0b", "") 
    while 8-len(binary)%8 < 8:
      binary = "0" + binary
    return binary
    
def bin_to_int(bin, bytes):
    ints = []
    for x in range(8, len(bin)+1, 8):
      ints.append(int(bin[x-8:x], 2))
    while len(ints) != bytes:
      ints.insert(0, 0)
    return ints


def send_chat(payload_decoded, username):
    payload_decoded['comment'] = secure_html(payload_decoded['comment'])
    payload_decoded['username'] = username
    outgoing_payload = json.dumps(payload_decoded)
    outgoing_payload_len = len(outgoing_payload)
    payload_decoded.pop('messageType')
    db.insert_chat(payload_decoded)

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


def chat_history(_, handler):
    history = [{"username": "user879", "comment": "hi 🚗"}, 
               {"username": "user222", "comment": "222"}]
    # history = db.list_all_chats()
    response = generate_response(json.dumps(history).encode(), "application/json; charset=utf-8", "200 OK")
    handler.request.sendall(response)