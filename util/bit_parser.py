

import json

closeconnection = '1000'
text_data = '0001'
binary_connection_data = '0010'

class WSBits:
    def __init__(self, rec_websocket_frame: bytes):

        self.websocket = {}

        self.rec_websocket_frame = rec_websocket_frame

        self.curr_ws_framebytes = self.rec_websocket_frame

    def getBits(ws_framebytes: bytes):
        bytelen = len(ws_framebytes)
        bitstr = format(int.from_bytes(ws_framebytes,'big'),'b')
        bitstr = bitstr.zfill(bytelen << 3)

        return bitstr


    def parse_opcode(self, ws_framebytes: bytes, popstr: bool = True) -> None:

        curr_byte = ws_framebytes[0]
        # print("opcode byte:", curr_byte, flush=True)
        get_opcode = curr_byte & BitsToInt('00001111')
        self.websocket["opcode"] = get_opcode

        # byte_str = getBytes(bits_str,1)

        # self.websocket["fin"] = byte_str[0]
        # self.websocket["rsv1"] = byte_str[1]
        # self.websocket["rsv2"] = byte_str[2]
        # self.websocket["rsv3"] = byte_str[3]
        
        # self.websocket["opcode"] = byte_str[4: ]

        if popstr:
            self.curr_ws_framebytes = self.curr_ws_framebytes[1: ]

        return

    def parse_mask_and_payloadlen(self, ws_framebytes: bytes, popstr: bool = True) -> None:

        curr_byte = ws_framebytes[0]
        
        get_mask = curr_byte & BitsToInt('10000000') # 128 if exists
        get_payload_len = curr_byte & BitsToInt('01111111')

        self.websocket["mask"] = get_mask
        self.websocket["payload-len"] = get_payload_len
        self.websocket["true-payload-len"] = get_payload_len

        print("LEN IS:", self.websocket["payload-len"], flush=True)

        # byte_str = getBytes(bits_str,1)

        # self.websocket["mask"] = byte_str[0]
        # self.websocket["payload-len"] = byte_str[1: ]

        if popstr:
            self.curr_ws_framebytes = self.curr_ws_framebytes[1: ]
        
        return

    def parse_extended_payloadlen(self, ws_framebytes: bytes, payload_len: int, popstr: bool = True) -> None:
        print("extending payload for", payload_len, flush=True)

        nBytes = 2 if payload_len == 126 else 8

        currbytes = ws_framebytes[ :nBytes]
        byteint = int.from_bytes(currbytes,'big')

        len_mask = '1' * (nBytes << 3)

        get_extended_payload_len = byteint & BitsToInt(len_mask)

        self.websocket["true-payload-len"] = get_extended_payload_len

        if popstr:
            self.curr_ws_framebytes = self.curr_ws_framebytes[nBytes: ]

        # if payload_len == 126:
        #     byte_str = getBytes(bits_str, 2)
        #     print(byte_str)
        #     self.websocket["payload-len"] = byte_str

        #     if popstr:
        #         two_bytes = 2*bytelen
        #         self._bitstr = self._bitstr[two_bytes: ]

        # elif payload_len == 127:
        #     print("127")
        #     byte_str = getBytes(bits_str, 8)
        #     self.websocket["payload-len"] = byte_str

        #     if popstr:
        #         self._bitstr = self._bitstr[8*bytelen: ]

        print("payload is:", self.websocket["payload-len"],"but true payload is:", self.websocket["true-payload-len"],flush=True)
        # print(self.websocket["true-payload-len"], flush=True)

        return

    def parse_maskingkey(self, ws_framebytes: bytes, popstr: bool = True) -> None:

        curr_bytes = ws_framebytes[ :4]
        byteint = int.from_bytes(curr_bytes,'big')
        
        key_mask = '1' * (4 << 3)
        get_maskingkey = byteint & BitsToInt(key_mask)

        self.websocket["masking-key"] = {}
        self.websocket["masking-key"]["bytes"] = curr_bytes
        self.websocket["masking-key"]["int"] = get_maskingkey

        # byte_str = getBytes(bits_str, 4)
        # self.websocket["masking-key"] = byte_str

        if popstr:
            self.curr_ws_framebytes = self.curr_ws_framebytes[4: ]

        return

    def parse_payload_data(self, ws_framebytes: bytes, payload_len: int, popstr: bool = True) -> None:
        print("parsing payload_data", payload_len, flush=True)
        # print(payload_len, flush=True)
        
        #bits_len = len(bits_str)
        payload_data = ws_framebytes[ :payload_len]

        self.websocket["payload-data"] = payload_data

        if popstr:
            self.curr_ws_framebytes = self.curr_ws_framebytes[len(payload_data): ]

        return

    def unmask_data(self, masking_key_bytes: bytes, payload_data_bytes: bytes) -> list:
        
        unmasked_payload_data = []

        # print(masking_key_bits)
        # print(payload_data_bits)

        #payload_len = self.ws.websocket["payload-len"]
        # n_payload_msgs = len(payload_data_bits) // four_bytes # divide by 32
        # payload_leftover = len(payload_data_bits) % four_bytes
        # payload_leftover = payload_leftover / bytelen
        # zfill left over

        masking_key = [key_byte for key_byte in masking_key_bytes]
        payload_data = [byte_data for byte_data in payload_data_bytes]
        # print(payload_data)

        # print(masking_key)
        # print(payload_data)

        for (i, byte) in enumerate(payload_data):
            # print(byte)
            keyi = i % 4

            # print("TEST", masking_key[keyi])
            unmasked_byte = masking_key[keyi] ^ byte

            unmasked_payload_data.append(unmasked_byte)
        


        # for i in range(n_payload_msgs):
            
        #     payload_data = BitsToInt(getBytes(payload_data_bitstr, 4))
        #     payload_data_bitstr = payload_data_bitstr[four_bytes: ]
        #     unmask = masking_key ^ payload_data
        #     unmask = format(unmask,'b').zfill(four_bytes)
        #     byteArr = toOrdArray(unmask,four_bytes)
        #     for byte in byteArr:
        #         unmasked_payload_data.append(byte)
        #     #print(masking_key_bits)
        #     #print(getBytes(payload_data_bitstr, 4))
        #     #print(unmask)
        #     #print()
        #     #unmasked_payload_data += unmask.encode()
        #     #unmasked_payload_data.append(unmask)

        # if len(payload_data_bitstr) > 0:

        #     payload_data_bitstr = payload_data_bitstr.zfill(four_bytes) #zfill to 32 and unmask
        #     print(payload_data_bitstr)

        #     payload_data = BitsToInt(payload_data_bitstr)
        #     payload_data_bitstr = payload_data_bitstr[four_bytes: ]
        #     unmask = masking_key ^ payload_data
        #     unmask = format(unmask,'b').zfill(four_bytes)
        #     byteArr = toOrdArray(unmask,four_bytes)
        #     for byte in byteArr:
        #         unmasked_payload_data.append(byte)
            #unmasked_payload_data += unmask.encode()
            #unmasked_payload_data.append(unmask)

        #print(unmasked_payload_data)

        #print("".join([chr(BitsToInt(ch)) for ch in unmasked_payload_data[:246]]))
        # payloadlen is for ascii payload_data only, not bytes

        return unmasked_payload_data

    def create_wsframe(self, opcode: int, json_dict: dict) -> bytes:
        wsframe = b''
        
        opcode_bits = '1000' + (format(opcode,'b').zfill(4))
        opcode_byte = BitsToInt(opcode_bits)


        json_str = (json.dumps(json_dict)).encode('ascii')
        json_len = len(json_str)
        if json_len >= 126 and json_len < 65536:
            self.websocket["payload-len"] = 126
            self.websocket["true-payload-len"] = json_len
        elif json_len >= 65536:
            self.websocket["payload-len"] = 127
            self.websocket["true-payload-len"] = json_len
        else:
            self.websocket["payload-len"] = json_len
            self.websocket["true-payload-len"] = json_len

        payload_len = self.websocket["payload-len"]
        mask_payloadlen_bits = '0' + (format(payload_len,'b').zfill(7)) # no mask bit

        mask_payloadlen_byte = BitsToInt(mask_payloadlen_bits)

        # print(mask_payloadlen_byte, flush=True)
        # print(payload_len, flush=True)

        wsframe += bytes([opcode_byte,mask_payloadlen_byte])

        # print("payload_len to pack is:", payload_len, self.websocket["true-payload-len"], flush=True)
        
        if payload_len == 126:
            extended_payload_len = self.websocket["true-payload-len"]
            # extended_payload_len_bits = format(extended_payload_len,'b').fill(16)
            # print("payload_len to pack is:", payload_len, flush=True)
            wsframe += extended_payload_len.to_bytes(2,'big')

        elif payload_len == 127:
            extended_payload_len = self.websocket["true-payload-len"]
            
            # print(extended_payload_len, flush=True)

            wsframe += extended_payload_len.to_bytes(8,'big')



        wsframe += json_str
        # print("remaining frame bytes:", self.curr_ws_framebytes[: 100], flush=True)


        return wsframe
        


        # if self.websocket["opcode"] == '0001': #TEXT

        #     data_dict["username"] = username

        # elif self.websocket["opcode"] == '0010': #BINARY
        #     binary_data = chrArr[payload_len: ]


def getBytes(bit_str: str, numOfBytes: int) -> str:
    n = numOfBytes << 3
    bits = bit_str[ :n]
    return bits

def toBits(theBytes: bytes, nBits: int = 8) -> str:
    ws_bits = ''
    for hexbyte in theBytes:
        ws_bits += format(hexbyte,'b').zfill(nBits)
    return ws_bits

def BitsToInt(bits: str) -> int:
    toInt = int(bits,2)
    return toInt

def toOrdArray(bitstr: str, n_bits: int = 32) -> list:
    byteArr = []
    n_bytes = n_bits//8
    for b in range(n_bytes):
        bits = b << 3
        bits_until = (b+1) << 3
        byteArr.append(BitsToInt(bitstr[bits:bits_until]))
    return byteArr