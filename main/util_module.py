import random

def genUUID(l) -> str:
    chars = "abcdefghijklmnopqrstuvwxyz1234567890"
    uuid = ''
    for c in range(l):
        uuid += random.choice(chars)
    return uuid