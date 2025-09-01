import os

def string_to_bits(s):
    return ''.join(format(ord(c), '08b') for c in s)

def bits_to_string(b):
    chars = [b[i:i+8] for i in range(0, len(b), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)

def generate_key(length):
    # Generate a truly random binary key same length as message bits
    return ''.join(str(int(x)) for x in os.urandom(length))

def xor_bits(a, b):
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))

# Original plaintext message
plaintext = "Hello, Quantum World!"

# Convert message to bits
plaintext_bits = string_to_bits(plaintext)
key = ''.join(str(bit) for bit in os.urandom(len(plaintext_bits)))
key_bits = ''.join(str(b % 2) for b in key.encode('latin1'))

# Generate random key of same length
key_bits = ''.join(str(int(x)) for x in os.urandom(len(plaintext_bits)))

# Encrypt (XOR plaintext with key)
ciphertext_bits = xor_bits(plaintext_bits, key_bits)

# Decrypt (XOR ciphertext with same key)
recovered_bits = xor_bits(ciphertext_bits, key_bits)

# Convert decrypted bits back to string
recovered_text = bits_to_string(recovered_bits)

print("Original:  ", plaintext)
print("Ciphertext (bits):", ciphertext_bits)
print("Recovered: ", recovered_text)

# The ciphertext is completely random without key
# and cannot be decrypted without the exact key.
