from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

# 1. Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024  # small for demo (easier for Shor); real-world uses 2048+
)
public_key = private_key.public_key()

# 2. Encrypt a message
message = b"15"
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("🔒 Encrypted Message (hex):", ciphertext.hex())

# 3. Decrypt the message
decrypted_message = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("🔓 Decrypted Message:", decrypted_message.decode())
