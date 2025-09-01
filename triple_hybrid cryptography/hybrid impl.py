#!/usr/bin/env python3
"""
Triple-Hybrid Cryptography Demonstration
----------------------------------------
This script demonstrates a hybrid key exchange using:
1. Classical (ECDH P-256)
2. Post-Quantum (Kyber768)
3. Quantum Key Distribution (BB84 simulation)

The three secrets are combined into a single master session key.
"""
import sys, os
PROJECT_ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_PATH)


from pqc.algorithms import get_algorithm
from qkd.bb84_simulator import BB84Simulator

import sys, os, hashlib

# ----------------------------------------------------------------------
# 1. Make sure Python can find your src/ directory
# ----------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(__file__)   # path to project folder
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_PATH)

# ----------------------------------------------------------------------
# 2. Import PQC + QKD implementations
# ----------------------------------------------------------------------
from pqc import get_algorithm
from qkd.bb84_simulator import BB84Simulator

# ----------------------------------------------------------------------
# 3. Helper function: combine secrets
# ----------------------------------------------------------------------
def combine_secrets(*secrets, out_len=32):
    """
    Combine multiple shared secrets into one master key.
    Uses SHA3-256 (HKDF-like).
    """
    hasher = hashlib.sha3_256()
    for s in secrets:
        hasher.update(s)
    return hasher.digest()[:out_len]

# ----------------------------------------------------------------------
# 4. Triple-Hybrid Handshake Demo
# ----------------------------------------------------------------------
def triple_hybrid_handshake():
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
    ss_qkd = qkd.generate_key(32)  # 32-byte quantum key
    print(f"✅ BB84 QKD key: {len(ss_qkd)} bytes")

    # --- Combine them into one master session key ---
    master_key = combine_secrets(ss_ecdh1, ss_kyber1, ss_qkd, out_len=32)
    print(f"\n🔑 Final Triple-Hybrid Master Key: {master_key.hex()}")
    print("============================================\n")
    print("Hybrid key successfully established using Classical + PQC + QKD")

# ----------------------------------------------------------------------
# 5. Run directly
# ----------------------------------------------------------------------
if __name__ == "__main__":
    triple_hybrid_handshake()
