import random

def genUUID(self, l) -> str:
    chars = "abcdefghijklmnopqrstuvwxyz1234567890"
    uuid = ''
    for c in range(l):
        uuid += random.choice(chars)
    return uuid