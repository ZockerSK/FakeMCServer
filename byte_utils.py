import struct


def read_varint(byte, i):
    result = 0
    bytes = 0
    while True:
        byte_in = byte[i]
        i += 1
        result |= (byte_in & 0x7F) << (bytes * 7)
        if bytes > 32:
            raise IOError("Packet is too long!")
        if (byte_in & 0x80) != 0x80:
            return result, i


def read_utf(byte, i):
    (length, i) = read_varint(byte, i)
    ip = byte[i:(i + length)].decode('utf-8')
    i += length
    return ip, i


def read_ushort(byte, i):
    new_i = i + 2
    return struct.unpack(">H", byte[i:new_i])[0], new_i


def read_long(byte, i):
    new_i = i + 8
    return struct.unpack(">q", byte[i:new_i]), new_i


def write_varint(byte, value):
    while True:
        part = value & 0x7F
        value >>= 7
        if value != 0:
            part |= 0x80
        byte.append(part)
        if value == 0:
            break


def write_utf(byte, value):
    write_varint(byte, len(value))
    for b in value.encode():
        byte.append(b)
