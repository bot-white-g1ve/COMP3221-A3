from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import json
from enum import Enum

def d_print(func, str):
    with open('debug.txt', 'a') as f:
        f.write(f"(In {func}) {str}\n")

ValidationError = Enum('ValidationError', ['VALID_TRANSACTION', 'VALID_REQUEST', 'INVALID_JSON', 'INVALID_TYPE', 'INVALID_SENDER', 'INVALID_MESSAGE', 'INVALID_NONCE', 'INVALID_SIGNATURE', 'INVALID_VALUES'])

def validate_transaction(payload):
    # Validate sender
    if not isinstance(payload["sender"], str) or len(payload["sender"]) != 64:
        return ValidationError.INVALID_SENDER
    # Validate message
    if not isinstance(payload["message"], str) or len(payload["message"]) > 70:
        return ValidationError.INVALID_MESSAGE
    # Validate nonce
    if not isinstance(payload["nonce"], int):
        return ValidationError.INVALID_NONCE
    # Validate signature
    if not isinstance(payload["signature"], str) or len(payload["signature"]) != 128:
        d_print("validation.validate_transaction", "the signature is not a valid string")
        return ValidationError.INVALID_SIGNATURE
    
    # Use signature to verify the message
    message_wo_sig = json.dumps({
        "sender": payload["sender"],
        "message": payload["message"],
        "nonce": payload["nonce"]},
        sort_keys=True)
    message_wo_sig_bytes = message_wo_sig.encode()
    signature_hex = payload["signature"]
    signature_bytes = bytes.fromhex(signature_hex)

    public_key_bytes = bytes.fromhex(payload["sender"])
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

    try:
        public_key.verify(signature_bytes, message_wo_sig_bytes)
    except Exception as e:
        d_print("validation.validate_transaction", "the signature is not corresponding to the message")
        return ValidationError.INVALID_SIGNATURE

    return ValidationError.VALID_TRANSACTION

def validate_values(payload):
    # For values, payload should be a number
    if not isinstance(payload, int):
        return ValidationError.INVALID_VALUES
    return ValidationError.VALID_REQUEST

def validate_message(message):
    if not isinstance(message, dict):
        d_print("validation.validate_message", "The message is not a dictionary")
        return ValidationError.INVALID_JSON
    if "type" not in message or "payload" not in message:
        d_print("validation.validate_message", "The message doesn't have key 'type' or 'payload'")
        return ValidationError.INVALID_JSON
    message_type = message["type"]
    payload = message["payload"]

    # Validate type
    if message_type not in ["transaction", "values"]:
        return ValidationError.INVALID_TYPE
    if message_type == "transaction":
        return validate_transaction(payload)
    elif message_type == "values":
        return validate_values(payload)
    
    return ValidationError.INVALID_JSON