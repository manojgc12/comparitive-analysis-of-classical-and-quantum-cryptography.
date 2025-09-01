from kyber_py.kyber import Kyber768
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

# Step 1: Kyber key exchange to get shared secret key
pk, sk = Kyber768.keygen()
shared_secret, ciphertext = Kyber768.encaps(pk)
recovered_secret = Kyber768.decaps(sk, ciphertext)
assert shared_secret == recovered_secret

# Step 2: Use shared_secret as AES key (trim if needed)
key = shared_secret[:16]  # Use first 16 bytes for AES-128

# Step 3: Encrypt the message with AES-GCM
plaintext = b"Hello good morning."
cipher = AES.new(key, AES.MODE_GCM)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)

print("Ciphertext:", ciphertext)
print("Nonce:", cipher.nonce)
print("Tag:", tag)

# Step 4: Decrypt using the same key
decipher = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
decrypted = decipher.decrypt_and_verify(ciphertext, tag)

print("Decrypted message:", decrypted.decode())
