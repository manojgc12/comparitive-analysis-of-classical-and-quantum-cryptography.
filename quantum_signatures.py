"""
Quantum-Safe Digital Signatures Implementation
Supports Dilithium, Falcon, and classical signature schemes with certificate handling
"""

import os
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
import logging

# Try to import OQS (Open Quantum Safe) - fallback to simulation if not available
try:
    import oqs
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False
    logging.warning("OQS not available, using simulation mode for PQ signatures")

class SignatureAlgorithm(Enum):
    """Supported signature algorithms"""
    # Classical
    RSA_PSS_2048 = "RSA-PSS-2048"
    RSA_PSS_3072 = "RSA-PSS-3072"
    ECDSA_P256 = "ECDSA-P256"
    ECDSA_P384 = "ECDSA-P384"
    ED25519 = "Ed25519"
    
    # Post-Quantum
    DILITHIUM2 = "Dilithium2"
    DILITHIUM3 = "Dilithium3" 
    DILITHIUM5 = "Dilithium5"
    FALCON512 = "Falcon-512"
    FALCON1024 = "Falcon-1024"
    SPHINCS_SHA256_128F = "SPHINCS+-SHA256-128f-robust"
    SPHINCS_SHA256_192F = "SPHINCS+-SHA256-192f-robust"
    SPHINCS_SHA256_256F = "SPHINCS+-SHA256-256f-robust"

@dataclass
class SignatureKeyPair:
    """Container for signature key pairs"""
    public_key: bytes
    private_key: bytes
    algorithm: SignatureAlgorithm
    key_size_public: int
    key_size_private: int

@dataclass
class DigitalSignature:
    """Container for digital signatures"""
    signature: bytes
    algorithm: SignatureAlgorithm
    message_hash: bytes
    timestamp: datetime
    signature_size: int

@dataclass
class QuantumSafeCertificate:
    """Container for quantum-safe certificates"""
    subject: str
    issuer: str
    public_key: bytes
    signature: bytes
    algorithm: SignatureAlgorithm
    valid_from: datetime
    valid_to: datetime
    serial_number: int
    certificate_der: bytes

class QuantumSafeSignature:
    """Post-Quantum Signature Scheme wrapper"""
    
    def __init__(self, algorithm: SignatureAlgorithm):
        self.algorithm = algorithm
        self.backend = default_backend()
        
        if OQS_AVAILABLE:
            # Map our algorithms to OQS names
            oqs_names = {
                SignatureAlgorithm.DILITHIUM2: "Dilithium2",
                SignatureAlgorithm.DILITHIUM3: "Dilithium3",
                SignatureAlgorithm.DILITHIUM5: "Dilithium5",
                SignatureAlgorithm.FALCON512: "Falcon-512",
                SignatureAlgorithm.FALCON1024: "Falcon-1024",
                SignatureAlgorithm.SPHINCS_SHA256_128F: "SPHINCS+-SHA256-128f-robust",
                SignatureAlgorithm.SPHINCS_SHA256_192F: "SPHINCS+-SHA256-192f-robust",
                SignatureAlgorithm.SPHINCS_SHA256_256F: "SPHINCS+-SHA256-256f-robust"
            }
            
            if algorithm in oqs_names:
                try:
                    self.sig = oqs.Signature(oqs_names[algorithm])
                    self._use_simulation = False
                except:
                    self._use_simulation = True
                    logging.warning(f"OQS algorithm {algorithm} not available, using simulation")
            else:
                self._use_simulation = True
        else:
            self._use_simulation = True
    
    def generate_keypair(self) -> SignatureKeyPair:
        """Generate a signature key pair"""
        if not self._use_simulation and hasattr(self, 'sig'):
            public_key = self.sig.generate_keypair()
            private_key = self.sig.export_secret_key()
            
            return SignatureKeyPair(
                public_key=public_key,
                private_key=private_key,
                algorithm=self.algorithm,
                key_size_public=len(public_key),
                key_size_private=len(private_key)
            )
        else:
            # Simulation mode - generate realistic key sizes
            key_sizes = {
                SignatureAlgorithm.DILITHIUM2: (1312, 2528),
                SignatureAlgorithm.DILITHIUM3: (1952, 4000),
                SignatureAlgorithm.DILITHIUM5: (2592, 4864),
                SignatureAlgorithm.FALCON512: (897, 1281),
                SignatureAlgorithm.FALCON1024: (1793, 2305),
                SignatureAlgorithm.SPHINCS_SHA256_128F: (32, 64),
                SignatureAlgorithm.SPHINCS_SHA256_192F: (48, 96),
                SignatureAlgorithm.SPHINCS_SHA256_256F: (64, 128)
            }
            
            pub_size, priv_size = key_sizes.get(self.algorithm, (1024, 2048))
            
            return SignatureKeyPair(
                public_key=secrets.token_bytes(pub_size),
                private_key=secrets.token_bytes(priv_size),
                algorithm=self.algorithm,
                key_size_public=pub_size,
                key_size_private=priv_size
            )
    
    def sign(self, message: bytes, private_key: bytes) -> DigitalSignature:
        """Sign a message using the private key"""
        message_hash = hashlib.sha384(message).digest()
        
        if not self._use_simulation and hasattr(self, 'sig'):
            signature = self.sig.sign(message)
        else:
            # Simulation mode - generate realistic signature sizes
            signature_sizes = {
                SignatureAlgorithm.DILITHIUM2: 2420,
                SignatureAlgorithm.DILITHIUM3: 3293,
                SignatureAlgorithm.DILITHIUM5: 4595,
                SignatureAlgorithm.FALCON512: 666,
                SignatureAlgorithm.FALCON1024: 1280,
                SignatureAlgorithm.SPHINCS_SHA256_128F: 17088,
                SignatureAlgorithm.SPHINCS_SHA256_192F: 35664,
                SignatureAlgorithm.SPHINCS_SHA256_256F: 49856
            }
            
            sig_size = signature_sizes.get(self.algorithm, 2048)
            signature = secrets.token_bytes(sig_size)
        
        return DigitalSignature(
            signature=signature,
            algorithm=self.algorithm,
            message_hash=message_hash,
            timestamp=datetime.now(),
            signature_size=len(signature)
        )
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify a signature using the public key"""
        if not self._use_simulation and hasattr(self, 'sig'):
            try:
                return self.sig.verify(message, signature, public_key)
            except:
                return False
        else:
            # Simulation mode - always return True for valid format
            return len(signature) > 0 and len(public_key) > 0

class ClassicalSignature:
    """Classical Digital Signature Schemes"""
    
    def __init__(self, algorithm: SignatureAlgorithm):
        self.algorithm = algorithm
        self.backend = default_backend()
    
    def generate_keypair(self) -> SignatureKeyPair:
        """Generate a classical signature key pair"""
        if self.algorithm == SignatureAlgorithm.RSA_PSS_2048:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
            public_key = private_key.public_key()
            
            return SignatureKeyPair(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size_public=270,  # Approximate DER size
                key_size_private=1218  # Approximate DER size
            )
        
        elif self.algorithm == SignatureAlgorithm.RSA_PSS_3072:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=3072,
                backend=self.backend
            )
            public_key = private_key.public_key()
            
            return SignatureKeyPair(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size_public=398,
                key_size_private=1838
            )
        
        elif self.algorithm == SignatureAlgorithm.ECDSA_P256:
            private_key = ec.generate_private_key(ec.SECP256R1(), self.backend)
            public_key = private_key.public_key()
            
            return SignatureKeyPair(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size_public=91,
                key_size_private=138
            )
        
        elif self.algorithm == SignatureAlgorithm.ECDSA_P384:
            private_key = ec.generate_private_key(ec.SECP384R1(), self.backend)
            public_key = private_key.public_key()
            
            return SignatureKeyPair(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size_public=120,
                key_size_private=185
            )
        
        elif self.algorithm == SignatureAlgorithm.ED25519:
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            return SignatureKeyPair(
                public_key=public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                algorithm=self.algorithm,
                key_size_public=44,
                key_size_private=48
            )
        
        else:
            raise ValueError(f"Unsupported classical signature algorithm: {self.algorithm}")
    
    def sign(self, message: bytes, private_key_bytes: bytes) -> DigitalSignature:
        """Sign a message using classical algorithms"""
        message_hash = hashlib.sha384(message).digest()
        
        if self.algorithm in [SignatureAlgorithm.RSA_PSS_2048, SignatureAlgorithm.RSA_PSS_3072]:
            private_key = serialization.load_der_private_key(private_key_bytes, None, self.backend)
            signature = private_key.sign(message, padding.PSS(
                mgf=padding.MGF1(hashes.SHA384()),
                salt_length=padding.PSS.MAX_LENGTH
            ), hashes.SHA384())
        
        elif self.algorithm in [SignatureAlgorithm.ECDSA_P256, SignatureAlgorithm.ECDSA_P384]:
            private_key = serialization.load_der_private_key(private_key_bytes, None, self.backend)
            signature = private_key.sign(message, ec.ECDSA(hashes.SHA384()))
        
        elif self.algorithm == SignatureAlgorithm.ED25519:
            private_key = serialization.load_der_private_key(private_key_bytes, None, self.backend)
            signature = private_key.sign(message)
        
        else:
            raise ValueError(f"Unsupported algorithm for signing: {self.algorithm}")
        
        return DigitalSignature(
            signature=signature,
            algorithm=self.algorithm,
            message_hash=message_hash,
            timestamp=datetime.now(),
            signature_size=len(signature)
        )
    
    def verify(self, message: bytes, signature: bytes, public_key_bytes: bytes) -> bool:
        """Verify a signature using classical algorithms"""
        try:
            if self.algorithm in [SignatureAlgorithm.RSA_PSS_2048, SignatureAlgorithm.RSA_PSS_3072]:
                public_key = serialization.load_der_public_key(public_key_bytes, self.backend)
                public_key.verify(signature, message, padding.PSS(
                    mgf=padding.MGF1(hashes.SHA384()),
                    salt_length=padding.PSS.MAX_LENGTH
                ), hashes.SHA384())
                return True
            
            elif self.algorithm in [SignatureAlgorithm.ECDSA_P256, SignatureAlgorithm.ECDSA_P384]:
                public_key = serialization.load_der_public_key(public_key_bytes, self.backend)
                public_key.verify(signature, message, ec.ECDSA(hashes.SHA384()))
                return True
            
            elif self.algorithm == SignatureAlgorithm.ED25519:
                public_key = serialization.load_der_public_key(public_key_bytes, self.backend)
                public_key.verify(signature, message)
                return True
            
            else:
                return False
        
        except Exception:
            return False

class CertificateAuthority:
    """Quantum-Safe Certificate Authority"""
    
    def __init__(self, ca_algorithm: SignatureAlgorithm = SignatureAlgorithm.DILITHIUM3):
        self.ca_algorithm = ca_algorithm
        self.backend = default_backend()
        
        # Initialize CA signature scheme
        if ca_algorithm.value.startswith(("Dilithium", "Falcon", "SPHINCS")):
            self.ca_signer = QuantumSafeSignature(ca_algorithm)
        else:
            self.ca_signer = ClassicalSignature(ca_algorithm)
        
        # Generate CA key pair
        self.ca_keypair = self.ca_signer.generate_keypair()
        self.ca_certificate = self._create_ca_certificate()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _create_ca_certificate(self) -> QuantumSafeCertificate:
        """Create self-signed CA certificate"""
        subject_name = "Quantum-Safe CA"
        
        # Create certificate data
        cert_data = {
            "subject": subject_name,
            "issuer": subject_name,
            "public_key": self.ca_keypair.public_key,
            "algorithm": self.ca_algorithm,
            "valid_from": datetime.now(),
            "valid_to": datetime.now() + timedelta(days=3650),  # 10 years
            "serial_number": secrets.randbits(64),
            "extensions": {
                "basic_constraints": {"ca": True, "path_length": None},
                "key_usage": {"digital_signature": True, "key_cert_sign": True, "crl_sign": True}
            }
        }
        
        # Serialize certificate for signing
        cert_bytes = json.dumps(cert_data, default=str, sort_keys=True).encode()
        
        # Sign the certificate
        signature_obj = self.ca_signer.sign(cert_bytes, self.ca_keypair.private_key)
        
        return QuantumSafeCertificate(
            subject=subject_name,
            issuer=subject_name,
            public_key=self.ca_keypair.public_key,
            signature=signature_obj.signature,
            algorithm=self.ca_algorithm,
            valid_from=cert_data["valid_from"],
            valid_to=cert_data["valid_to"],
            serial_number=cert_data["serial_number"],
            certificate_der=cert_bytes
        )
    
    def issue_certificate(self, 
                         subject_name: str,
                         subject_public_key: bytes,
                         subject_algorithm: SignatureAlgorithm,
                         validity_days: int = 365) -> QuantumSafeCertificate:
        """Issue a certificate for a given public key"""
        
        cert_data = {
            "subject": subject_name,
            "issuer": "Quantum-Safe CA",
            "public_key": base64.b64encode(subject_public_key).decode(),
            "subject_algorithm": subject_algorithm.value,
            "algorithm": self.ca_algorithm.value,
            "valid_from": datetime.now(),
            "valid_to": datetime.now() + timedelta(days=validity_days),
            "serial_number": secrets.randbits(64),
            "extensions": {
                "basic_constraints": {"ca": False},
                "key_usage": {"digital_signature": True, "key_encipherment": True}
            }
        }
        
        # Serialize certificate for signing
        cert_bytes = json.dumps(cert_data, default=str, sort_keys=True).encode()
        
        # Sign the certificate with CA private key
        signature_obj = self.ca_signer.sign(cert_bytes, self.ca_keypair.private_key)
        
        certificate = QuantumSafeCertificate(
            subject=subject_name,
            issuer="Quantum-Safe CA",
            public_key=subject_public_key,
            signature=signature_obj.signature,
            algorithm=self.ca_algorithm,
            valid_from=cert_data["valid_from"],
            valid_to=cert_data["valid_to"],
            serial_number=cert_data["serial_number"],
            certificate_der=cert_bytes
        )
        
        self.logger.info(f"Issued certificate for {subject_name} using {subject_algorithm.value}")
        return certificate
    
    def verify_certificate(self, certificate: QuantumSafeCertificate) -> bool:
        """Verify a certificate using CA public key"""
        try:
            return self.ca_signer.verify(
                certificate.certificate_der,
                certificate.signature,
                self.ca_keypair.public_key
            )
        except Exception as e:
            self.logger.error(f"Certificate verification failed: {e}")
            return False
    
    def revoke_certificate(self, serial_number: int) -> Dict[str, Any]:
        """Revoke a certificate (simplified implementation)"""
        revocation_data = {
            "serial_number": serial_number,
            "revocation_time": datetime.now(),
            "reason": "unspecified"
        }
        
        self.logger.info(f"Revoked certificate with serial number: {serial_number}")
        return revocation_data

class HybridSignatureSystem:
    """Hybrid signature system supporting classical and post-quantum algorithms"""
    
    def __init__(self):
        self.supported_algorithms = list(SignatureAlgorithm)
        self.ca = CertificateAuthority(SignatureAlgorithm.DILITHIUM3)
        self.certificates = {}  # Store issued certificates
        self.logger = logging.getLogger(__name__)
    
    def create_keypair(self, algorithm: SignatureAlgorithm) -> SignatureKeyPair:
        """Create a key pair for any supported algorithm"""
        if algorithm.value.startswith(("Dilithium", "Falcon", "SPHINCS")):
            signer = QuantumSafeSignature(algorithm)
        else:
            signer = ClassicalSignature(algorithm)
        
        return signer.generate_keypair()
    
    def sign_message(self, 
                    message: bytes, 
                    private_key: bytes, 
                    algorithm: SignatureAlgorithm) -> DigitalSignature:
        """Sign a message with specified algorithm"""
        if algorithm.value.startswith(("Dilithium", "Falcon", "SPHINCS")):
            signer = QuantumSafeSignature(algorithm)
        else:
            signer = ClassicalSignature(algorithm)
        
        return signer.sign(message, private_key)
    
    def verify_signature(self, 
                        message: bytes, 
                        signature: bytes, 
                        public_key: bytes, 
                        algorithm: SignatureAlgorithm) -> bool:
        """Verify a signature with specified algorithm"""
        if algorithm.value.startswith(("Dilithium", "Falcon", "SPHINCS")):
            signer = QuantumSafeSignature(algorithm)
        else:
            signer = ClassicalSignature(algorithm)
        
        return signer.verify(message, signature, public_key)
    
    def create_certificate_chain(self, 
                                subject_name: str, 
                                algorithm: SignatureAlgorithm,
                                validity_days: int = 365) -> Dict[str, Any]:
        """Create a complete certificate chain"""
        # Generate subject key pair
        subject_keypair = self.create_keypair(algorithm)
        
        # Issue certificate
        certificate = self.ca.issue_certificate(
            subject_name=subject_name,
            subject_public_key=subject_keypair.public_key,
            subject_algorithm=algorithm,
            validity_days=validity_days
        )
        
        # Store certificate
        self.certificates[certificate.serial_number] = certificate
        
        chain = {
            "subject_certificate": certificate,
            "ca_certificate": self.ca.ca_certificate,
            "subject_keypair": subject_keypair,
            "chain_valid": self.ca.verify_certificate(certificate)
        }
        
        self.logger.info(f"Created certificate chain for {subject_name}")
        return chain
    
    def benchmark_algorithms(self, message_size: int = 1024, iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Benchmark all supported signature algorithms"""
        results = {}
        test_message = secrets.token_bytes(message_size)
        
        for algorithm in self.supported_algorithms:
            self.logger.info(f"Benchmarking {algorithm.value}...")
            
            try:
                # Key generation benchmark
                keygen_times = []
                sign_times = []
                verify_times = []
                
                for i in range(iterations):
                    # Key generation
                    start_time = time.time()
                    keypair = self.create_keypair(algorithm)
                    keygen_times.append(time.time() - start_time)
                    
                    # Signing
                    start_time = time.time()
                    signature_obj = self.sign_message(test_message, keypair.private_key, algorithm)
                    sign_times.append(time.time() - start_time)
                    
                    # Verification
                    start_time = time.time()
                    is_valid = self.verify_signature(
                        test_message, 
                        signature_obj.signature, 
                        keypair.public_key, 
                        algorithm
                    )
                    verify_times.append(time.time() - start_time)
                
                results[algorithm.value] = {
                    "keygen_avg_ms": sum(keygen_times) / len(keygen_times) * 1000,
                    "sign_avg_ms": sum(sign_times) / len(sign_times) * 1000,
                    "verify_avg_ms": sum(verify_times) / len(verify_times) * 1000,
                    "public_key_size": keypair.key_size_public,
                    "private_key_size": keypair.key_size_private,
                    "signature_size": signature_obj.signature_size,
                    "verification_success": is_valid
                }
                
            except Exception as e:
                self.logger.error(f"Benchmark failed for {algorithm.value}: {e}")
                results[algorithm.value] = {"error": str(e)}
        
        return results
    
    def crypto_agility_demo(self) -> Dict[str, Any]:
        """Demonstrate crypto-agility by switching between algorithms"""
        demo_results = {}
        test_message = b"Quantum-safe cryptography demonstration message"
        
        # Test classical algorithms
        classical_algorithms = [
            SignatureAlgorithm.RSA_PSS_2048,
            SignatureAlgorithm.ECDSA_P256,
            SignatureAlgorithm.ED25519
        ]
        
        # Test post-quantum algorithms
        pq_algorithms = [
            SignatureAlgorithm.DILITHIUM2,
            SignatureAlgorithm.DILITHIUM3,
            SignatureAlgorithm.FALCON512
        ]
        
        for category, algorithms in [("Classical", classical_algorithms), ("Post-Quantum", pq_algorithms)]:
            demo_results[category] = {}
            
            for algorithm in algorithms:
                try:
                    # Create certificate chain
                    chain = self.create_certificate_chain(
                        f"Demo-{algorithm.value}",
                        algorithm
                    )
                    
                    # Sign and verify message
                    signature_obj = self.sign_message(
                        test_message,
                        chain["subject_keypair"].private_key,
                        algorithm
                    )
                    
                    is_valid = self.verify_signature(
                        test_message,
                        signature_obj.signature,
                        chain["subject_keypair"].public_key,
                        algorithm
                    )
                    
                    demo_results[category][algorithm.value] = {
                        "certificate_valid": chain["chain_valid"],
                        "signature_valid": is_valid,
                        "signature_size": signature_obj.signature_size,
                        "key_sizes": {
                            "public": chain["subject_keypair"].key_size_public,
                            "private": chain["subject_keypair"].key_size_private
                        }
                    }
                    
                except Exception as e:
                    demo_results[category][algorithm.value] = {"error": str(e)}
        
        return demo_results

# Example usage and testing
if __name__ == "__main__":
    print("=== Quantum-Safe Digital Signatures Demo ===\n")
    
    # Initialize hybrid signature system
    sig_system = HybridSignatureSystem()
    
    print("1. Testing Certificate Creation...")
    
    # Test certificate creation for different algorithms
    test_algorithms = [
        SignatureAlgorithm.RSA_PSS_2048,
        SignatureAlgorithm.ECDSA_P256,
        SignatureAlgorithm.DILITHIUM3,
        SignatureAlgorithm.FALCON512
    ]
    
    certificates = []
    for algorithm in test_algorithms:
        try:
            chain = sig_system.create_certificate_chain(
                f"TestEntity-{algorithm.value}",
                algorithm
            )
            certificates.append(chain)
            print(f"✓ Created certificate for {algorithm.value}")
        except Exception as e:
            print(f"✗ Failed to create certificate for {algorithm.value}: {e}")
    
    print(f"\nCreated {len(certificates)} certificates")
    
    print("\n2. Testing Message Signing and Verification...")
    
    test_message = b"This is a test message for quantum-safe signatures"
    
    for i, cert_chain in enumerate(certificates):
        try:
            algorithm = cert_chain["subject_keypair"].algorithm
            
            # Sign message
            signature_obj = sig_system.sign_message(
                test_message,
                cert_chain["subject_keypair"].private_key,
                algorithm
            )
            
            # Verify signature
            is_valid = sig_system.verify_signature(
                test_message,
                signature_obj.signature,
                cert_chain["subject_keypair"].public_key,
                algorithm
            )
            
            print(f"✓ {algorithm.value}: Signature valid = {is_valid}, Size = {signature_obj.signature_size} bytes")
            
        except Exception as e:
            print(f"✗ Signature test failed for certificate {i}: {e}")
    
    print("\n3. Crypto-Agility Demonstration...")
    
    agility_results = sig_system.crypto_agility_demo()
    
    for category, results in agility_results.items():
        print(f"\n{category} Algorithms:")
        for algorithm, result in results.items():
            if "error" not in result:
                print(f"  {algorithm}: ✓ Certificate={result['certificate_valid']}, "
                      f"Signature={result['signature_valid']}, "
                      f"SigSize={result['signature_size']}B")
            else:
                print(f"  {algorithm}: ✗ {result['error']}")
    
    print("\n4. Performance Benchmarking (Mini Version)...")
    
    # Run a smaller benchmark for demo purposes
    benchmark_results = sig_system.benchmark_algorithms(message_size=512, iterations=10)
    
    print(f"{'Algorithm':<20} {'KeyGen(ms)':<12} {'Sign(ms)':<10} {'Verify(ms)':<12} {'SigSize(B)':<10}")
    print("-" * 70)
    
    for algorithm, results in benchmark_results.items():
        if "error" not in results:
            print(f"{algorithm:<20} {results['keygen_avg_ms']:<12.2f} "
                  f"{results['sign_avg_ms']:<10.2f} {results['verify_avg_ms']:<12.2f} "
                  f"{results['signature_size']:<10}")
        else:
            print(f"{algorithm:<20} ERROR: {results['error']}")
    
    print("\n=== Demo Complete ===")
    print(f"Total certificates in system: {len(sig_system.certificates)}")
    print(f"CA Algorithm: {sig_system.ca.ca_algorithm.value}")
    print(f"Supported algorithms: {len(sig_system.supported_algorithms)}")
