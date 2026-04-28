import hashlib
def hash(data: tuple):
    return hashlib.sha256(data.encode()).hexdigest()