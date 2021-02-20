from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from base64 import b64encode, b64decode


def generate_key():
    return ECC.generate(curve='P-256')


def import_key(filename):
    try:
        with open(filename, 'r') as f:
            return ECC.import_key(f.read())

    except (FileNotFoundError, ValueError):
        return None


def export_key(key, filename):
        with open(filename,'w') as f:
            f.write(key.export_key(format='PEM'))


def string_to_key(string):
    return ECC.import_key(b64decode(string.encode()))


def key_to_string(key):
    return b64encode(key.export_key(format='DER')).decode()


def sign_message(key, message):
    h = SHA256.new(message.encode())
    signer = DSS.new(key, 'fips-186-3')
    return b64encode(signer.sign(h)).decode()


def validate_signature(key, message, signature):
    h = SHA256.new(message.encode())
    verifier = DSS.new(key, 'fips-186-3')
    signature = b64decode(signature.encode())
    try:
        verifier.verify(h, signature)
        return True
    except ValueError:
        return False


def sha256(x):
    return b64encode(SHA256.new(x.encode()).digest()).decode()

