import json

# test = b"zKyj5z76FHrJjKkDLJ/6Hg=="

# guid = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

# web = test + guid

# output = "GYVPzWpCxGj2RfAb61I+7t4Yn6k="

# hash_obj = hashlib.sha1(web)
# hash_object = hashlib.sha1(web)
# pbHash = hash_object.hexdigest()
# # length = len(pbHash.decode("hex"))
# print(pbHash.decode("hex"))
# payload_decoded = '{"messageType":"chatMessage","comment":"sad"}'
# payload_decoded = json.loads(payload_decoded)
# print(payload_decoded)

# payload_decoded = {"messageType":"chatMessage","comment":"sad", "username": "User5458"}
# payload_decoded = json.dumps(payload_decoded)
# print(payload_decoded)
# print(len(payload_decoded))



# def to_bin(dec):
#     binary = bin(dec).replace("0b", "") 
#     while 8-len(binary)%8 < 8:
#       binary = "0" + binary
#     return binary
    
# def bin_to_int(bin, bytes):
#     ints = []
#     for x in range(8, len(bin)+1, 8):
#       print(x)
#       ints.append(int(bin[x-8:x], 2))
#     while len(ints) != bytes:
#       ints.insert(0, 0)
#     return ints

# bin = str(to_bin(65537))
# print(bin)
# ins = bin_to_int(bin, 8)
# print(ins)


# test = bytes([129, "5"])
# print(test)

# msg_type == "webRTC-offer" or "webRTC-answer" or "webRTC-candidate":
# msg_type = "webRTC-offer"
# print("rtc", msg_type[7:])

# newdict = {9:0, 2:0, 3:0}

test = [1, 2, 3, 4]
for x in test:
    if x == 2:
        test.insert(2, 20)
    print(x)


tick = {}
tick[1] = {2: [3]}  # ex: {1: {router: n}}
print(tick)
