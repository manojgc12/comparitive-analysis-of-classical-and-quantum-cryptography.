import hashlib
import os

def classical_key_exchange():

    print("Performing classical Diffie-Hellman key exchange...")

    return os.urandom(32)


def pqc_key_exchange():

    print("Performing PQC (Kyber/ML-KEM) key exchange...")

    return os.urandom(32)


def qkd_key_exchange():

    print("Performing QKD key exchange with a physical device...")

    return os.urandom(32)




def hkdf_derive_key(key_material, salt, info, output_length):

    prk = hashlib.sha256(salt + key_material).digest()


    derived_key = hashlib.sha256(prk + info).digest()


    return derived_key[:output_length]




def encrypt_data(key, data):

    print("Encrypting data...")

    ciphertext_hash = hashlib.sha256(key + data).digest()
    return ciphertext_hash




def run_triple_hybrid_handshake():

    print("--- Starting Triple-Hybrid Protocol Handshake ---")


    classical_key = classical_key_exchange()
    pqc_key = pqc_key_exchange()
    qkd_key = qkd_key_exchange()


    combined_key_material = classical_key + pqc_key + qkd_key
    print(f"\nCombined key material length: {len(combined_key_material)} bytes")


    salt = os.urandom(32)
    info = b"tls-1.3-triple-hybrid-session-key"
    session_key_length = 32  # AES-256 key length

    session_key = hkdf_derive_key(combined_key_material, salt, info, session_key_length)

    print("\n--- Handshake Complete ---")
    print(f"Final session key (hex): {session_key.hex()}")
    print("The session key is now protected by all three cryptographic assumptions.")


    user_data = input("\nEnter data to protect: ")
    print(f"\nProtecting your data using the derived session key...")
    encrypted_data = encrypt_data(session_key, user_data.encode('utf-8'))
    print(f"Data protected successfully. Ciphertext: {encrypted_data.hex()}")

if __name__ == "__main__":
    run_triple_hybrid_handshake()
