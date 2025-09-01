"""
rsa_toy_encrypt_input.py
Educational RSA toy encryption demo (small primes only).
User inputs a number as the message.
"""


def modular_inverse(a, m):
    """Return modular inverse of a mod m using Extended Euclidean Algorithm."""

    def egcd(a, b):
        if b == 0:
            return (a, 1, 0)
        g, x1, y1 = egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m


def generate_toy_rsa(p, q, e, message_int):
    # Step 1: Compute n and phi(n)
    n = p * q
    phi = (p - 1) * (q - 1)

    # Step 2: Compute private exponent d
    d = modular_inverse(e, phi)
    if d is None:
        raise ValueError("e has no modular inverse mod phi(n). Choose a different e.")

    if message_int >= n:
        raise ValueError(f"Message integer {message_int} must be smaller than modulus n={n}.")

    # Step 3: Encrypt
    c = pow(message_int, e, n)

    # Step 4: Decrypt (for check)
    m_dec = pow(c, d, n)

    return {
        "p": p, "q": q,
        "n": n, "phi": phi,
        "e": e, "d": d,
        "plaintext_int": message_int,
        "ciphertext": c,
        "decrypted_int": m_dec
    }


if __name__ == "__main__":
    print("=== RSA Toy Encryption Demo ===")

    # Fixed small primes for demo
    p, q, e = 3, 5, 7

    # User input
    try:
        m = int(input("Enter a number as the plaintext message (must be < n=15): ").strip())
    except Exception:
        print("Invalid input.")
        exit(1)

    result = generate_toy_rsa(p, q, e, m)

    print("\n--- Results ---")
    print(f"Primes: p={result['p']}, q={result['q']}")
    print(f"n = {result['n']}, phi(n) = {result['phi']}")
    print(f"Public key: (n={result['n']}, e={result['e']})")
    print(f"Private key: (n={result['n']}, d={result['d']})")
    print(f"Plaintext (int): {result['plaintext_int']}")
    print(f"Ciphertext (c = m^e mod n): {result['ciphertext']}")
    print(f"Decrypted (c^d mod n): {result['decrypted_int']}")
