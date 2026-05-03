import hmac
import hashlib
import base64

def hash(data,hash_key):

    signature = base64.b64encode(
        hmac.new(
            hash_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    return signature