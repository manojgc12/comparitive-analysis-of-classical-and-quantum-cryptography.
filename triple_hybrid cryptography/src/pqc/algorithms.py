import hashlib


def get_algorithm(name):
    return DummyAlgorithm(name)


class DummyAlgorithm:
    def __init__(self, name):
        self.name = name
        self._last_secret = None  # store last shared secret

    def keygen(self):
        pub = b"public_key_" + self.name.encode()
        priv = b"private_key_" + self.name.encode()
        return pub, priv

    def encapsulate(self, pub_key):
        # Shared secret derived deterministically
        shared_secret = hashlib.sha256(self.name.encode() + b"_shared").digest()
        ciphertext = b"cipher_" + self.name.encode()
        # Save it so decapsulate can return same value
        self._last_secret = shared_secret
        return ciphertext, shared_secret

    def decapsulate(self, priv_key, ciphertext):
        # Return same secret generated during encapsulate
        if self._last_secret is None:
            raise ValueError("No encapsulation done yet")
        return self._last_secret

    def get_algorithm_info(self):
        return {"name": self.name, "quantum_safe": "kyber" in self.name}
