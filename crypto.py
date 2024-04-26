from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def generate_keypair_bytes():
    '''
    Generate a keypair in bytes form
    '''
    # generate Ed25519 private key
    private_key = ed25519.Ed25519PrivateKey.generate()

    # generate public key from private key
    public_key = private_key.public_key()

    # serialize private key to bytes
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    # serialize public key to bytes
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    # return both keys in bytes
    return private_bytes, public_bytes

def publickey_bytes_to_hex(public_key_bytes):
    # load public key from bytes
    loaded_public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)

    # transform to hex
    public_key_hex = loaded_public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()

    return public_key_hex