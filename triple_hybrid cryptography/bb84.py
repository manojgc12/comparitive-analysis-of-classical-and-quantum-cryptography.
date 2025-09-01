import hashlib
import os
from typing import Tuple


# --- PART 1: SIMULATING THE KEY EXCHANGE MECHANISMS ---
# The paper describes a real-world implementation using OpenSSL, strongSwan, and liboqs.
# These functions are placeholders that simulate the output of those complex operations.
# The keys are represented as random bytes.

def classical_key_exchange() -> bytes:
    """
    Simulates a classical key exchange (e.g., Diffie-Hellman).
    Returns 32 bytes of raw key material.
    """
    print("Performing classical Diffie-Hellman key exchange...")
    return os.urandom(32)


def pqc_key_exchange() -> bytes:
    """
    Simulates a Post-Quantum Cryptography (PQC) key exchange (e.g., Kyber/ML-KEM).
    Returns 32 bytes of raw key material.
    """
    print("Performing PQC (Kyber/ML-KEM) key exchange...")
    return os.urandom(32)


def qkd_key_exchange() -> bytes:
    """
    Simulates a Quantum Key Distribution (QKD) key exchange.
    Returns 32 bytes of raw key material from a key management system.
    """
    print("Performing QKD key exchange with a physical device...")
    return os.urandom(32)


# --- PART 2: SIMULATING THE HKDF KEY DERIVATION FUNCTION (RFC 5869) ---
# The paper mentions that TLS 1.3 uses a concatenation approach followed by HKDF.
# This implementation reflects the two main steps of HKDF: HKDF-Extract and HKDF-Expand.

def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    """
    The HKDF-Extract function, which produces a pseudo-random key (PRK).
    Args:
        salt (bytes): A random value. Can be set to a zero-length string if not provided.
        ikm (bytes): The input key material.
    Returns:
        bytes: A pseudo-random key (PRK) of 32 bytes.
    """
    if not salt:
        salt = b'\x00' * 32
    return hashlib.sha256(salt + ikm).digest()


def hkdf_expand(prk: bytes, info: bytes, output_length: int) -> bytes:
    """
    The HKDF-Expand function, which derives keys from the PRK.
    Args:
        prk (bytes): The pseudo-random key from HKDF-Extract.
        info (bytes): A context-specific label.
        output_length (int): The desired length of the output key in bytes.
    Returns:
        bytes: The derived key.
    """
    hash_len = hashlib.sha256().digest_size
    n = (output_length + hash_len - 1) // hash_len
    t = b""
    okm = b""
    for i in range(1, n + 1):
        t = hashlib.sha256(t + prk + info + bytes([i])).digest()
        okm += t
    return okm[:output_length]


# --- PART 3: SIMULATING DATA PROTECTION ---
# This part simulates the encryption and decryption of data using the derived session key.
# It is important to note that these are simplified placeholder functions.
# A real implementation would use a secure symmetric cipher like AES-256-GCM.

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes]:
    """
    Simulates the encryption of data using the session key.
    Returns a tuple of (ciphertext, tag). This is a placeholder.
    Note: This is for demonstration only and is not cryptographically secure.
    """
    print("Encrypting data with the session key...")
    # A real implementation would use a library like 'cryptography'.
    # Example: AES.new(key, AES.MODE_GCM)

    # We simulate a ciphertext and an authentication tag using hashes.
    ciphertext = hashlib.sha256(key + data).digest()
    tag = hashlib.sha256(ciphertext).digest()  # A dummy tag
    return ciphertext, tag


def decrypt_data(key: bytes, ciphertext: bytes, tag: bytes) -> bytes:
    """
    Simulates the decryption of data using the session key.
    Returns the decrypted plaintext. This is a placeholder.
    Note: This is for demonstration only.
    """
    print("Decrypting data with the session key...")
    # In a real scenario, you would verify the tag before decrypting.
    # We will simulate the decryption by hashing the key and ciphertext to get the original data.
    # This is a reverse-engineered and insecure simulation.
    return b"Decrypted Data: This is a placeholder for the original plaintext."


# --- PART 4: THE MAIN LOGIC FOR THE TRIPLE-HYBRID PROTOCOL ---

def run_triple_hybrid_handshake():
    """
    This function orchestrates the entire simulated handshake.
    It performs the three key exchanges, combines the keys, and
    derives a final session key.
    """
    print("--- Starting Triple-Hybrid Protocol Handshake ---")

    # 1. Perform each key exchange. The paper mentions concatenation for TLS.
    classical_key = classical_key_exchange()
    pqc_key = pqc_key_exchange()
    qkd_key = qkd_key_exchange()

    # 2. Combine the raw key material by concatenation.
    # This is the "IKM" (Input Key Material) for the HKDF.
    combined_key_material = classical_key + pqc_key + qkd_key
    print(f"\nCombined key material length: {len(combined_key_material)} bytes")

    # 3. Use the combined material to derive the final session key using HKDF.
    salt = os.urandom(32)  # The paper mentions using a salt.
    info = b"tls-1.3-triple-hybrid-session-key"  # A context-specific label.
    session_key_length = 32  # AES-256 key length, as mentioned in the paper.

    prk = hkdf_extract(salt, combined_key_material)
    session_key = hkdf_expand(prk, info, session_key_length)

    print("\n--- Handshake Complete ---")
    print(f"Final session key (hex): {session_key.hex()}")
    print("The session key is now protected by all three cryptographic assumptions.")

    # 4. Get user input and protect it with the new session key.
    user_data = input("\nEnter data to protect: ")
    user_data_bytes = user_data.encode('utf-8')

    ciphertext, tag = encrypt_data(session_key, user_data_bytes)
    print(f"\nData protected successfully. Ciphertext: {ciphertext.hex()}")
    print(f"Authentication Tag: {tag.hex()}...")

    # 5. Simulate decryption to retrieve the original data.
    decrypted_data = decrypt_data(session_key, ciphertext, tag)
    print(f"\nOriginal data retrieved: {decrypted_data.decode('utf-8')}")


# Entry point for the simulation
if __name__ == "__main__":
    run_triple_hybrid_handshake()
