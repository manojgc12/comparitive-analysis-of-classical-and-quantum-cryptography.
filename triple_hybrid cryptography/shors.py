"""
shor_rsa_decrypt.py

Educational demo: Use Qiskit's Shor algorithm (simulator) to factor a small RSA modulus
and decrypt a ciphertext.

NOTE:
- Only works for tiny RSA moduli (like n=15, 21, 33, ...).
- For larger numbers the simulator will be too slow.
"""

from qiskit import Aer
from qiskit.utils import QuantumInstance
from qiskit.algorithms import Shor

# Toy RSA public key
N = 15   # modulus
E = 7    # public exponent

def modular_inverse(a, m):
    """Return modular inverse of a mod m."""
    def egcd(a, b):
        if b == 0:
            return (a, 1, 0)
        g, x1, y1 = egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def decrypt_rsa(n, e, c, p, q):
    """Decrypt RSA ciphertext using factors (p, q)."""
    phi = (p - 1) * (q - 1)
    d = modular_inverse(e, phi)
    if d is None:
        raise ValueError("No modular inverse for e mod phi(n)")
    m = pow(c, d, n)
    return d, m

def factor_with_shor(n):
    """Factor n using Qiskit's Shor algorithm on simulator."""
    backend = Aer.get_backend("aer_simulator")
    qi = QuantumInstance(backend=backend, shots=1)
    shor = Shor()
    result = shor.factor(n, quantum_instance=qi)
    if result.factors:
        p, q = result.factors[0]
        return int(p), int(q)
    raise ValueError("Shor failed to find factors")

def main():
    print("=== RSA Decryption with Shor's Algorithm (Qiskit) ===")
    c = int(input("Enter ciphertext (integer): ").strip())

    print(f"[INFO] Factoring N={N} using Shor's algorithm...")
    p, q = factor_with_shor(N)
    print(f"[OK] Factors of N={N}: p={p}, q={q}")

    d, m = decrypt_rsa(N, E, c, p, q)
    print(f"[RESULT] private exponent d = {d}")
    print(f"[RESULT] decrypted integer m = {m}")

if __name__ == "__main__":
    main()
