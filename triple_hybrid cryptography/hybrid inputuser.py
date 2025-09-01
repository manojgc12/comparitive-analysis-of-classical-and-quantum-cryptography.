#!/usr/bin/env python3
"""
Triple-Hybrid Cryptography Demonstration (with user input)
----------------------------------------------------------
This script demonstrates a hybrid key exchange using:
1. Classical (ECDH P-256)
2. Post-Quantum (Kyber768)
3. Quantum Key Distribution (BB84 simulation)

The three secrets are combined into a single master session key.
Then, the user provides a text message which is encrypted/decrypted
with that hybrid master key using AES-GCM.
"""

import sys, os, hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# ----------------------------------------------------------------------
# 1. Add src/ folder to path (for pqc + qkd modules)
# ----------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_PATH)

# Import PQC + QKD implementations
from pqc import get_algorithm
from qkd.bb84_simulator import BB84Simulator

# ----------------------------------------------------------------------
# 2. Helper: combine secrets into one key
# ----------------------------------------------------------------------
def combine_secrets(*secrets, out_len=32):
    hasher = hashlib.sha3_256()
    for s in secrets:
        hasher.update(s)
    return hasher.digest()[:out_len]

# ----------------------------------------------------------------------
# 3. AES-GCM Encryption/Decryption
# ----------------------------------------------------------------------
def encrypt_message(key, plaintext):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return cipher.nonce, ciphertext, tag

def decrypt_message(key, nonce, ciphertext, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

# ----------------------------------------------------------------------
# 4. Triple-Hybrid Handshake + Message Encryption
# ----------------------------------------------------------------------
def triple_hybrid_demo():
    print("\n🔐 Triple-Hybrid Cryptography Demonstration")
    print("============================================")

    # --- Classical: ECDH ---
    ecdh = get_algorithm("ecdh_p256")
    pub_ecdh, priv_ecdh = ecdh.keygen()
    ct_ecdh, ss_ecdh1 = ecdh.encapsulate(pub_ecdh)
    ss_ecdh2 = ecdh.decapsulate(priv_ecdh, ct_ecdh)
    assert ss_ecdh1 == ss_ecdh2
    print(f"✅ ECDH P-256 shared secret: {len(ss_ecdh1)} bytes")

    # --- Post-Quantum: Kyber768 ---
    kyber = get_algorithm("kyber768")
    pub_kyber, priv_kyber = kyber.keygen()
    ct_kyber, ss_kyber1 = kyber.encapsulate(pub_kyber)
    ss_kyber2 = kyber.decapsulate(priv_kyber, ct_kyber)
    assert ss_kyber1 == ss_kyber2
    print(f"✅ Kyber768 shared secret: {len(ss_kyber1)} bytes")

    # --- Quantum: BB84 QKD Simulation ---
    qkd = BB84Simulator(error_rate=0.01, channel_loss=0.1)
    ss_qkd = qkd.generate_key(32)
    print(f"✅ BB84 QKD key: {len(ss_qkd)} bytes")

    # --- Combine all into one hybrid key ---
    master_key = combine_secrets(ss_ecdh1, ss_kyber1, ss_qkd, out_len=32)
    print(f"\n🔑 Final Triple-Hybrid Master Key: {master_key.hex()}")
    print("============================================")

    # --- User input for message ---
    message = input("\n💬 Enter a message to encrypt: ")

    # Encrypt with AES-GCM
    nonce, ciphertext, tag = encrypt_message(master_key, message)
    print(f"\n🔒 Encrypted Message (hex): {ciphertext.hex()}")

    # Decrypt with AES-GCM
    decrypted = decrypt_message(master_key, nonce, ciphertext, tag)
    print(f"🔓 Decrypted Message: {decrypted}")

    print("\n✅ Triple-hybrid encryption & decryption successful!")

# ----------------------------------------------------------------------
# 5. Run demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    triple_hybrid_demo()
