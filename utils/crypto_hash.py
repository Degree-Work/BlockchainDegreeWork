from hashlib import sha256


def crypto_hash(*args):
    content = ' '.join(map(str, args))
    content_hash = sha256(content.encode())
    return content_hash.hexdigest()


def binary_representation(value):
    result = ""
    for i in value:
        if i == '0':
            result += "0000"
        elif i == '1':
            result += "0001"
        elif i == '2':
            result += "0010"
        elif i == '3':
            result += "0011"
        elif i == '4':
            result += "0100"
        elif i == '5':
            result += "0101"
        elif i == '6':
            result += "0110"
        elif i == '7':
            result += "0111"
        elif i == '8':
            result += "1000"
        elif i == '9':
            result += "1001"
        elif i == 'a' or i == 'A':
            result += "1010"
        elif i == 'b' or i == 'B':
            result += "1011"
        elif i == 'c' or i == 'C':
            result += "1100"
        elif i == 'd' or i == 'D':
            result += "1101"
        elif i == 'e' or i == 'E':
            result += "1110"
        elif i == 'f' or i == 'F':
            result += "1111"
    return result
