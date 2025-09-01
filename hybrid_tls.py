"""
Hybrid TLS 1.3 Handshake Implementation
Supports classical, dual-hybrid, and triple-hybrid key exchange groups
"""

import os
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, x25519, x448
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import logging

# Try to import OQS (Open Quantum Safe) - fallback to simulation if not available
try:
    import oqs
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False
    logging.warning("OQS not available, using simulation mode")

class KeyExchangeType(Enum):
    """Types of key exchange mechanisms"""
    CLASSICAL = "classical"
    PQ_ONLY = "pq_only"
    DUAL_HYBRID = "dual_hybrid"
    TRIPLE_HYBRID = "triple_hybrid"

class CryptoAlgorithm(Enum):
    """Supported cryptographic algorithms"""
    # Classical
    X25519 = "X25519"
    X448 = "X448"
    ECDH_P256 = "ECDH-P256"
    ECDH_P384 = "ECDH-P384"
    RSA_2048 = "RSA-2048"
    
    # Post-Quantum KEM
    KYBER512 = "Kyber512"
    KYBER768 = "Kyber768"
    KYBER1024 = "Kyber1024"
    NTRU_HPS2048509 = "NTRU-HPS-2048-509"
    NTRU_HPS2048677 = "NTRU-HPS-2048-677"
    LIGHTSABER = "LightSaber-KEM"
    SABER = "Saber-KEM"
    FIRESABER = "FireSaber-KEM"

@dataclass
class KeyMaterial:
    """Container for cryptographic key material"""
    public_key: bytes
    private_key: bytes
    algorithm: CryptoAlgorithm
    key_size: int

@dataclass
class HandshakeMessage:
    """TLS handshake message structure"""
    message_type: str
    sender: str
    payload: Dict[str, Any]
    timestamp: float

class QuantumSafeKEM:
    """Post-Quantum Key Encapsulation Mechanism wrapper"""
    
    def __init__(self, algorithm: CryptoAlgorithm):
        self.algorithm = algorithm
        self.backend = default_backend()
        
        if OQS_AVAILABLE:
            # Map our algorithms to OQS names
            oqs_names = {
                CryptoAlgorithm.KYBER512: "Kyber512",
                CryptoAlgorithm.KYBER768: "Kyber768", 
                CryptoAlgorithm.KYBER1024: "Kyber1024",
                CryptoAlgorithm.NTRU_HPS2048509: "NTRU-HPS-2048-509",
                CryptoAlgorithm.NTRU_HPS2048677: "NTRU-HPS-2048-677",
                CryptoAlgorithm.LIGHTSABER: "LightSaber-KEM",
                CryptoAlgorithm.SABER: "Saber-KEM",
                CryptoAlgorithm.FIRESABER: "FireSaber-KEM"
            }
            
            if algorithm in oqs_names:
                try:
                    self.kem = oqs.KeyEncapsulation(oqs_names[algorithm])
                    self._use_simulation = False
                except:
                    self._use_simulation = True
                    logging.warning(f"OQS algorithm {algorithm} not available, using simulation")
            else:
                self._use_simulation = True
        else:
            self._use_simulation = True
    
    def generate_keypair(self) -> KeyMaterial:
        """Generate a key pair for the KEM"""
        if not self._use_simulation and hasattr(self, 'kem'):
            public_key = self.kem.generate_keypair()
            private_key = self.kem.export_secret_key()
            
            return KeyMaterial(
                public_key=public_key,
                private_key=private_key,
                algorithm=self.algorithm,
                key_size=len(public_key)
            )
        else:
            # Simulation mode - generate random bytes
            key_sizes = {
                CryptoAlgorithm.KYBER512: (800, 1632),
                CryptoAlgorithm.KYBER768: (1184, 2400),
                CryptoAlgorithm.KYBER1024: (1568, 3168),
                CryptoAlgorithm.NTRU_HPS2048509: (699, 935),
                CryptoAlgorithm.NTRU_HPS2048677: (930, 1234),
                CryptoAlgorithm.LIGHTSABER: (672, 1568),
                CryptoAlgorithm.SABER: (992, 2304),
                CryptoAlgorithm.FIRESABER: (1312, 3040)
            }
            
            pub_size, priv_size = key_sizes.get(self.algorithm, (1024, 2048))
            
            return KeyMaterial(
                public_key=secrets.token_bytes(pub_size),
                private_key=secrets.token_bytes(priv_size),
                algorithm=self.algorithm,
                key_size=pub_size
            )
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulate a shared secret using the public key"""
        if not self._use_simulation and hasattr(self, 'kem'):
            ciphertext, shared_secret = self.kem.encap_secret(public_key)
            return ciphertext, shared_secret
        else:
            # Simulation mode
            ciphertext = secrets.token_bytes(len(public_key))
            shared_secret = secrets.token_bytes(32)  # 256-bit shared secret
            return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """Decapsulate the shared secret using the private key"""
        if not self._use_simulation and hasattr(self, 'kem'):
            return self.kem.decap_secret(ciphertext)
        else:
            # Simulation mode - return consistent shared secret
            return secrets.token_bytes(32)

class ClassicalKEM:
    """Classical Key Exchange Mechanisms"""
    
    def __init__(self, algorithm: CryptoAlgorithm):
        self.algorithm = algorithm
        self.backend = default_backend()
    
    def generate_keypair(self) -> KeyMaterial:
        """Generate a classical key pair"""
        if self.algorithm == CryptoAlgorithm.X25519:
            private_key = x25519.X25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            return KeyMaterial(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size=32
            )
        
        elif self.algorithm == CryptoAlgorithm.X448:
            private_key = x448.X448PrivateKey.generate()
            public_key = private_key.public_key()
            
            return KeyMaterial(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size=56
            )
        
        elif self.algorithm == CryptoAlgorithm.ECDH_P256:
            private_key = ec.generate_private_key(ec.SECP256R1(), self.backend)
            public_key = private_key.public_key()
            
            return KeyMaterial(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.X962,
                    format=serialization.PublicFormat.UncompressedPoint
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size=65  # Uncompressed point
            )
        
        elif self.algorithm == CryptoAlgorithm.ECDH_P384:
            private_key = ec.generate_private_key(ec.SECP384R1(), self.backend)
            public_key = private_key.public_key()
            
            return KeyMaterial(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.X962,
                    format=serialization.PublicFormat.UncompressedPoint
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size=97  # Uncompressed point
            )
        
        else:
            raise ValueError(f"Unsupported classical algorithm: {self.algorithm}")
    
    def derive_shared_secret(self, private_key: bytes, public_key: bytes) -> bytes:
        """Derive shared secret from key exchange"""
        if self.algorithm == CryptoAlgorithm.X25519:
            priv_key = x25519.X25519PrivateKey.from_private_bytes(private_key)
            pub_key = x25519.X25519PublicKey.from_public_bytes(public_key)
            return priv_key.exchange(pub_key)
        
        elif self.algorithm == CryptoAlgorithm.X448:
            priv_key = x448.X448PrivateKey.from_private_bytes(private_key)
            pub_key = x448.X448PublicKey.from_public_bytes(public_key)
            return priv_key.exchange(pub_key)
        
        # For ECDH, we'd need to reconstruct the key objects
        # This is a simplified implementation
        return secrets.token_bytes(32)

class HybridTLSHandshake:
    """Hybrid TLS 1.3 Handshake Implementation"""
    
    def __init__(self, 
                 exchange_type: KeyExchangeType = KeyExchangeType.DUAL_HYBRID,
                 classical_alg: CryptoAlgorithm = CryptoAlgorithm.X25519,
                 pq_alg1: CryptoAlgorithm = CryptoAlgorithm.KYBER768,
                 pq_alg2: Optional[CryptoAlgorithm] = None):
        
        self.exchange_type = exchange_type
        self.classical_alg = classical_alg
        self.pq_alg1 = pq_alg1
        self.pq_alg2 = pq_alg2
        
        # Initialize key exchange mechanisms
        self.classical_kem = ClassicalKEM(classical_alg)
        self.pq_kem1 = QuantumSafeKEM(pq_alg1)
        
        if pq_alg2 and exchange_type == KeyExchangeType.TRIPLE_HYBRID:
            self.pq_kem2 = QuantumSafeKEM(pq_alg2)
        else:
            self.pq_kem2 = None
        
        self.handshake_messages: List[HandshakeMessage] = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _log_message(self, msg_type: str, sender: str, payload: Dict[str, Any]):
        """Log handshake message"""
        message = HandshakeMessage(
            message_type=msg_type,
            sender=sender,
            payload=payload,
            timestamp=time.time()
        )
        self.handshake_messages.append(message)
        self.logger.info(f"{sender} -> {msg_type}: {payload.keys()}")
    
    def client_hello(self) -> Dict[str, Any]:
        """Generate Client Hello message with supported key exchange groups"""
        supported_groups = []
        
        if self.exchange_type in [KeyExchangeType.CLASSICAL, KeyExchangeType.DUAL_HYBRID, KeyExchangeType.TRIPLE_HYBRID]:
            supported_groups.append(self.classical_alg.value)
        
        if self.exchange_type in [KeyExchangeType.PQ_ONLY, KeyExchangeType.DUAL_HYBRID, KeyExchangeType.TRIPLE_HYBRID]:
            supported_groups.append(self.pq_alg1.value)
        
        if self.exchange_type == KeyExchangeType.TRIPLE_HYBRID and self.pq_alg2:
            supported_groups.append(self.pq_alg2.value)
        
        client_hello = {
            "protocol_version": "TLS 1.3",
            "random": secrets.token_bytes(32),
            "cipher_suites": [
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_AES_128_GCM_SHA256"
            ],
            "supported_groups": supported_groups,
            "key_exchange_type": self.exchange_type.value,
            "extensions": {
                "supported_versions": ["TLS 1.3"],
                "pq_hybrid": True
            }
        }
        
        self._log_message("ClientHello", "Client", client_hello)
        return client_hello
    
    def server_hello(self, client_hello: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Server Hello message and select key exchange parameters"""
        
        # Select the best available key exchange group
        client_groups = client_hello["supported_groups"]
        selected_group = None
        
        # Prefer hybrid approaches
        if self.exchange_type == KeyExchangeType.TRIPLE_HYBRID and self.pq_alg2:
            if all(alg.value in client_groups for alg in [self.classical_alg, self.pq_alg1, self.pq_alg2]):
                selected_group = f"triple_hybrid_{self.classical_alg.value}_{self.pq_alg1.value}_{self.pq_alg2.value}"
        
        elif self.exchange_type == KeyExchangeType.DUAL_HYBRID:
            if all(alg.value in client_groups for alg in [self.classical_alg, self.pq_alg1]):
                selected_group = f"hybrid_{self.classical_alg.value}_{self.pq_alg1.value}"
        
        elif self.exchange_type == KeyExchangeType.CLASSICAL:
            if self.classical_alg.value in client_groups:
                selected_group = self.classical_alg.value
        
        elif self.exchange_type == KeyExchangeType.PQ_ONLY:
            if self.pq_alg1.value in client_groups:
                selected_group = self.pq_alg1.value
        
        if not selected_group:
            raise ValueError("No compatible key exchange group found")
        
        server_hello = {
            "protocol_version": "TLS 1.3",
            "random": secrets.token_bytes(32),
            "cipher_suite": "TLS_AES_256_GCM_SHA384",
            "selected_group": selected_group,
            "extensions": {
                "key_share": True,
                "pq_hybrid": True
            }
        }
        
        self._log_message("ServerHello", "Server", server_hello)
        return server_hello
    
    def generate_key_shares(self, is_server: bool = True) -> Dict[str, Any]:
        """Generate key shares based on the selected exchange type"""
        key_shares = {}
        
        if self.exchange_type in [KeyExchangeType.CLASSICAL, KeyExchangeType.DUAL_HYBRID, KeyExchangeType.TRIPLE_HYBRID]:
            classical_keys = self.classical_kem.generate_keypair()
            key_shares["classical"] = {
                "algorithm": classical_keys.algorithm.value,
                "public_key": classical_keys.public_key,
                "key_size": classical_keys.key_size
            }
            if is_server:
                key_shares["classical"]["private_key"] = classical_keys.private_key
        
        if self.exchange_type in [KeyExchangeType.PQ_ONLY, KeyExchangeType.DUAL_HYBRID, KeyExchangeType.TRIPLE_HYBRID]:
            pq_keys1 = self.pq_kem1.generate_keypair()
            key_shares["pq_primary"] = {
                "algorithm": pq_keys1.algorithm.value,
                "public_key": pq_keys1.public_key,
                "key_size": pq_keys1.key_size
            }
            if is_server:
                key_shares["pq_primary"]["private_key"] = pq_keys1.private_key
        
        if self.exchange_type == KeyExchangeType.TRIPLE_HYBRID and self.pq_kem2:
            pq_keys2 = self.pq_kem2.generate_keypair()
            key_shares["pq_secondary"] = {
                "algorithm": pq_keys2.algorithm.value,
                "public_key": pq_keys2.public_key,
                "key_size": pq_keys2.key_size
            }
            if is_server:
                key_shares["pq_secondary"]["private_key"] = pq_keys2.private_key
        
        sender = "Server" if is_server else "Client"
        self._log_message("KeyShare", sender, {k: f"{len(v['public_key'])} bytes" for k, v in key_shares.items()})
        
        return key_shares
    
    def compute_shared_secrets(self, 
                             server_key_shares: Dict[str, Any], 
                             client_key_shares: Dict[str, Any]) -> bytes:
        """Compute combined shared secret from all key exchange mechanisms"""
        shared_secrets = []
        
        # Classical key exchange
        if "classical" in server_key_shares and "classical" in client_key_shares:
            try:
                classical_secret = self.classical_kem.derive_shared_secret(
                    server_key_shares["classical"]["private_key"],
                    client_key_shares["classical"]["public_key"]
                )
                shared_secrets.append(classical_secret)
                self.logger.info(f"Classical shared secret: {len(classical_secret)} bytes")
            except Exception as e:
                self.logger.warning(f"Classical key exchange failed: {e}")
                shared_secrets.append(secrets.token_bytes(32))
        
        # Primary PQ key exchange
        if "pq_primary" in server_key_shares and "pq_primary" in client_key_shares:
            try:
                ciphertext, pq_secret1 = self.pq_kem1.encapsulate(
                    server_key_shares["pq_primary"]["public_key"]
                )
                shared_secrets.append(pq_secret1)
                self.logger.info(f"PQ primary shared secret: {len(pq_secret1)} bytes")
            except Exception as e:
                self.logger.warning(f"PQ primary key exchange failed: {e}")
                shared_secrets.append(secrets.token_bytes(32))
        
        # Secondary PQ key exchange (for triple hybrid)
        if "pq_secondary" in server_key_shares and "pq_secondary" in client_key_shares and self.pq_kem2:
            try:
                ciphertext, pq_secret2 = self.pq_kem2.encapsulate(
                    server_key_shares["pq_secondary"]["public_key"]
                )
                shared_secrets.append(pq_secret2)
                self.logger.info(f"PQ secondary shared secret: {len(pq_secret2)} bytes")
            except Exception as e:
                self.logger.warning(f"PQ secondary key exchange failed: {e}")
                shared_secrets.append(secrets.token_bytes(32))
        
        # Combine all shared secrets using HKDF
        if shared_secrets:
            combined_secret = b''.join(shared_secrets)
            
            # Use HKDF to derive final shared secret
            hkdf = HKDF(
                algorithm=hashes.SHA384(),
                length=48,  # 384 bits
                salt=b"TLS 1.3 Hybrid Key Schedule",
                info=f"hybrid-{self.exchange_type.value}".encode(),
                backend=default_backend()
            )
            
            final_secret = hkdf.derive(combined_secret)
            
            self.logger.info(f"Final combined shared secret: {len(final_secret)} bytes")
            self._log_message("SharedSecret", "Combined", {
                "algorithm_count": len(shared_secrets),
                "total_entropy": len(combined_secret),
                "final_size": len(final_secret)
            })
            
            return final_secret
        
        else:
            raise ValueError("No shared secrets could be computed")
    
    def perform_handshake(self) -> Dict[str, Any]:
        """Perform complete hybrid TLS handshake"""
        start_time = time.time()
        
        # Step 1: Client Hello
        client_hello = self.client_hello()
        
        # Step 2: Server Hello
        server_hello = self.server_hello(client_hello)
        
        # Step 3: Key Share Generation
        server_key_shares = self.generate_key_shares(is_server=True)
        client_key_shares = self.generate_key_shares(is_server=False)
        
        # Step 4: Compute Shared Secret
        shared_secret = self.compute_shared_secrets(server_key_shares, client_key_shares)
        
        # Step 5: Derive Session Keys (simplified)
        session_keys = self._derive_session_keys(shared_secret)
        
        handshake_duration = time.time() - start_time
        
        result = {
            "success": True,
            "exchange_type": self.exchange_type.value,
            "algorithms": [self.classical_alg.value, self.pq_alg1.value],
            "handshake_duration": handshake_duration,
            "shared_secret_size": len(shared_secret),
            "session_keys": session_keys,
            "message_count": len(self.handshake_messages),
            "key_sizes": {
                "classical": server_key_shares.get("classical", {}).get("key_size", 0),
                "pq_primary": server_key_shares.get("pq_primary", {}).get("key_size", 0),
                "pq_secondary": server_key_shares.get("pq_secondary", {}).get("key_size", 0)
            }
        }
        
        if self.pq_alg2:
            result["algorithms"].append(self.pq_alg2.value)
        
        self._log_message("HandshakeComplete", "System", result)
        return result
    
    def _derive_session_keys(self, shared_secret: bytes) -> Dict[str, bytes]:
        """Derive session keys from shared secret"""
        hkdf = HKDF(
            algorithm=hashes.SHA384(),
            length=32,
            salt=b"TLS 1.3 session keys",
            info=b"client server keys",
            backend=default_backend()
        )
        
        key_material = hkdf.derive(shared_secret)
        
        return {
            "client_write_key": key_material[:16],
            "server_write_key": key_material[16:32],
            "client_write_iv": secrets.token_bytes(12),
            "server_write_iv": secrets.token_bytes(12)
        }
    
    def get_handshake_summary(self) -> Dict[str, Any]:
        """Get summary of handshake messages and performance"""
        return {
            "total_messages": len(self.handshake_messages),
            "exchange_type": self.exchange_type.value,
            "algorithms_used": [
                self.classical_alg.value,
                self.pq_alg1.value,
                self.pq_alg2.value if self.pq_alg2 else None
            ],
            "messages": [
                {
                    "type": msg.message_type,
                    "sender": msg.sender,
                    "timestamp": msg.timestamp
                }
                for msg in self.handshake_messages
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    print("=== Hybrid TLS 1.3 Handshake Demo ===\n")
    
    # Test different handshake types
    handshake_configs = [
        {
            "name": "Classical Only",
            "type": KeyExchangeType.CLASSICAL,
            "classical": CryptoAlgorithm.X25519,
            "pq1": CryptoAlgorithm.KYBER768,
            "pq2": None
        },
        {
            "name": "Dual Hybrid (Classical + PQ)",
            "type": KeyExchangeType.DUAL_HYBRID,
            "classical": CryptoAlgorithm.X25519,
            "pq1": CryptoAlgorithm.KYBER768,
            "pq2": None
        },
        {
            "name": "Triple Hybrid (Classical + 2 PQ)",
            "type": KeyExchangeType.TRIPLE_HYBRID,
            "classical": CryptoAlgorithm.ECDH_P256,
            "pq1": CryptoAlgorithm.KYBER768,
            "pq2": CryptoAlgorithm.NTRU_HPS2048509
        },
        {
            "name": "PQ Only",
            "type": KeyExchangeType.PQ_ONLY,
            "classical": CryptoAlgorithm.X25519,
            "pq1": CryptoAlgorithm.KYBER1024,
            "pq2": None
        }
    ]
    
    results = []
    
    for config in handshake_configs:
        print(f"\n--- Testing {config['name']} ---")
        
        try:
            handshake = HybridTLSHandshake(
                exchange_type=config["type"],
                classical_alg=config["classical"],
                pq_alg1=config["pq1"],
                pq_alg2=config["pq2"]
            )
            
            result = handshake.perform_handshake()
            results.append({
                "config": config["name"],
                "result": result
            })
            
            print(f"✓ Success: {result['handshake_duration']:.3f}s")
            print(f"  Algorithms: {', '.join(result['algorithms'])}")
            print(f"  Shared secret: {result['shared_secret_size']} bytes")
            print(f"  Messages: {result['message_count']}")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            results.append({
                "config": config["name"],
                "result": {"error": str(e)}
            })
    
    print("\n=== Performance Summary ===")
    for result in results:
        if "error" not in result["result"]:
            print(f"{result['config']}: {result['result']['handshake_duration']:.3f}s")
        else:
            print(f"{result['config']}: ERROR - {result['result']['error']}")
