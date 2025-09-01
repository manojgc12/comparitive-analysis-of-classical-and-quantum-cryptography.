"""
Extended Post-Quantum Algorithm Support
Implements additional NIST candidates and alternative PQ schemes beyond the core algorithms
"""

import secrets
import hashlib
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

# Try to import additional cryptographic libraries
try:
    from Crypto.Hash import SHA256, SHA3_256, SHAKE256, BLAKE2s
    from Crypto.Cipher import AES
    PYCRYPTO_AVAILABLE = True
except ImportError:
    PYCRYPTO_AVAILABLE = False

class PQAlgorithmFamily(Enum):
    """Post-quantum algorithm families"""
    LATTICE_BASED = "lattice"
    CODE_BASED = "code"
    MULTIVARIATE = "multivariate"
    HASH_BASED = "hash"
    ISOGENY_BASED = "isogeny"  # Note: SIKE was broken
    SYMMETRIC = "symmetric"

class SecurityLevel(Enum):
    """NIST security levels"""
    LEVEL_1 = 1  # Equivalent to AES-128
    LEVEL_3 = 3  # Equivalent to AES-192
    LEVEL_5 = 5  # Equivalent to AES-256

@dataclass
class AlgorithmParameters:
    """Parameters for a post-quantum algorithm"""
    name: str
    family: PQAlgorithmFamily
    security_level: SecurityLevel
    key_sizes: Dict[str, int]  # public_key, private_key, signature
    performance_characteristics: Dict[str, Any]
    standardization_status: str  # "NIST_Standard", "NIST_Candidate", "Alternative"
    implementation_notes: str

class ExtendedNTRUImplementation:
    """Extended NTRU implementation with multiple parameter sets"""
    
    def __init__(self, parameter_set: str = "hps2048509"):
        self.parameter_set = parameter_set
        
        # NTRU parameter sets
        self.parameters = {
            "hps2048509": {
                "n": 509,
                "q": 2048,
                "public_key_size": 699,
                "private_key_size": 935,
                "ciphertext_size": 699,
                "security_level": SecurityLevel.LEVEL_1
            },
            "hps2048677": {
                "n": 677,
                "q": 2048,
                "public_key_size": 930,
                "private_key_size": 1234,
                "ciphertext_size": 930,
                "security_level": SecurityLevel.LEVEL_3
            },
            "hps4096821": {
                "n": 821,
                "q": 4096,
                "public_key_size": 1230,
                "private_key_size": 1590,
                "ciphertext_size": 1230,
                "security_level": SecurityLevel.LEVEL_5
            },
            "hrss701": {
                "n": 701,
                "q": 8192,
                "public_key_size": 1138,
                "private_key_size": 1450,
                "ciphertext_size": 1138,
                "security_level": SecurityLevel.LEVEL_1
            }
        }
        
        if parameter_set not in self.parameters:
            raise ValueError(f"Unknown NTRU parameter set: {parameter_set}")
        
        self.params = self.parameters[parameter_set]
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate NTRU key pair (simulation)"""
        # In a real implementation, this would generate proper NTRU lattice keys
        public_key = secrets.token_bytes(self.params["public_key_size"])
        private_key = secrets.token_bytes(self.params["private_key_size"])
        
        return public_key, private_key
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """NTRU encapsulation (simulation)"""
        if len(public_key) != self.params["public_key_size"]:
            raise ValueError("Invalid public key size")
        
        shared_secret = secrets.token_bytes(32)  # 256-bit shared secret
        ciphertext = secrets.token_bytes(self.params["ciphertext_size"])
        
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """NTRU decapsulation (simulation)"""
        if len(ciphertext) != self.params["ciphertext_size"]:
            raise ValueError("Invalid ciphertext size")
        if len(private_key) != self.params["private_key_size"]:
            raise ValueError("Invalid private key size")
        
        # In simulation, return consistent shared secret
        return hashlib.sha256(ciphertext + private_key).digest()[:32]

class SPHINCSPlusImplementation:
    """SPHINCS+ implementation with multiple parameter sets"""
    
    def __init__(self, parameter_set: str = "sphincs-sha256-128f-robust"):
        self.parameter_set = parameter_set
        
        # SPHINCS+ parameter sets
        self.parameters = {
            "sphincs-sha256-128f-robust": {
                "security_level": SecurityLevel.LEVEL_1,
                "hash_function": "SHA256",
                "variant": "robust",
                "public_key_size": 32,
                "private_key_size": 64,
                "signature_size": 17088,
                "tree_height": 66,
                "winternitz_parameter": 16
            },
            "sphincs-sha256-128s-robust": {
                "security_level": SecurityLevel.LEVEL_1,
                "hash_function": "SHA256",
                "variant": "robust",
                "public_key_size": 32,
                "private_key_size": 64,
                "signature_size": 7856,
                "tree_height": 63,
                "winternitz_parameter": 16
            },
            "sphincs-sha256-192f-robust": {
                "security_level": SecurityLevel.LEVEL_3,
                "hash_function": "SHA256",
                "variant": "robust",
                "public_key_size": 48,
                "private_key_size": 96,
                "signature_size": 35664,
                "tree_height": 66,
                "winternitz_parameter": 16
            },
            "sphincs-sha256-256f-robust": {
                "security_level": SecurityLevel.LEVEL_5,
                "hash_function": "SHA256",
                "variant": "robust",
                "public_key_size": 64,
                "private_key_size": 128,
                "signature_size": 49856,
                "tree_height": 68,
                "winternitz_parameter": 16
            },
            "sphincs-shake256-128f-robust": {
                "security_level": SecurityLevel.LEVEL_1,
                "hash_function": "SHAKE256",
                "variant": "robust",
                "public_key_size": 32,
                "private_key_size": 64,
                "signature_size": 17088,
                "tree_height": 66,
                "winternitz_parameter": 16
            }
        }
        
        if parameter_set not in self.parameters:
            raise ValueError(f"Unknown SPHINCS+ parameter set: {parameter_set}")
        
        self.params = self.parameters[parameter_set]
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate SPHINCS+ key pair (simulation)"""
        # SPHINCS+ uses a random seed to generate the key pair
        seed = secrets.token_bytes(self.params["private_key_size"])
        
        # Public key is derived from private key
        if self.params["hash_function"] == "SHA256":
            public_key = hashlib.sha256(seed).digest()[:self.params["public_key_size"]]
        else:  # SHAKE256
            public_key = hashlib.shake_256(seed).digest(self.params["public_key_size"])
        
        return public_key, seed
    
    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """SPHINCS+ signature generation (simulation)"""
        if len(private_key) != self.params["private_key_size"]:
            raise ValueError("Invalid private key size")
        
        # In a real implementation, this would perform the SPHINCS+ signing process
        # involving multiple hash tree levels and Winternitz one-time signatures
        
        message_hash = hashlib.sha256(message).digest()
        signature_material = private_key + message_hash
        
        # Generate signature of appropriate size
        signature = bytearray()
        for i in range(0, self.params["signature_size"], 32):
            chunk = hashlib.sha256(signature_material + i.to_bytes(4, 'big')).digest()
            signature.extend(chunk[:min(32, self.params["signature_size"] - len(signature))])
        
        return bytes(signature)
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """SPHINCS+ signature verification (simulation)"""
        if len(signature) != self.params["signature_size"]:
            return False
        if len(public_key) != self.params["public_key_size"]:
            return False
        
        # In simulation, perform basic consistency checks
        message_hash = hashlib.sha256(message).digest()
        
        # Verify signature format and basic properties
        if len(signature) == self.params["signature_size"]:
            return True  # Simplified verification for simulation
        
        return False

class FrodoKEMImplementation:
    """FrodoKEM implementation - Learning with Errors based KEM"""
    
    def __init__(self, parameter_set: str = "FrodoKEM-640-AES"):
        self.parameter_set = parameter_set
        
        # FrodoKEM parameter sets
        self.parameters = {
            "FrodoKEM-640-AES": {
                "n": 640,
                "m": 8,
                "security_level": SecurityLevel.LEVEL_1,
                "public_key_size": 9616,
                "private_key_size": 19888,
                "ciphertext_size": 9720,
                "shared_secret_size": 16,
                "noise_distribution": "rounded_gaussian"
            },
            "FrodoKEM-976-AES": {
                "n": 976,
                "m": 8,
                "security_level": SecurityLevel.LEVEL_3,
                "public_key_size": 15632,
                "private_key_size": 31296,
                "ciphertext_size": 15744,
                "shared_secret_size": 24,
                "noise_distribution": "rounded_gaussian"
            },
            "FrodoKEM-1344-AES": {
                "n": 1344,
                "m": 8,
                "security_level": SecurityLevel.LEVEL_5,
                "public_key_size": 21520,
                "private_key_size": 43088,
                "ciphertext_size": 21632,
                "shared_secret_size": 32,
                "noise_distribution": "rounded_gaussian"
            }
        }
        
        if parameter_set not in self.parameters:
            raise ValueError(f"Unknown FrodoKEM parameter set: {parameter_set}")
        
        self.params = self.parameters[parameter_set]
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate FrodoKEM key pair (simulation)"""
        public_key = secrets.token_bytes(self.params["public_key_size"])
        private_key = secrets.token_bytes(self.params["private_key_size"])
        
        return public_key, private_key
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """FrodoKEM encapsulation (simulation)"""
        if len(public_key) != self.params["public_key_size"]:
            raise ValueError("Invalid public key size")
        
        shared_secret = secrets.token_bytes(self.params["shared_secret_size"])
        ciphertext = secrets.token_bytes(self.params["ciphertext_size"])
        
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """FrodoKEM decapsulation (simulation)"""
        if len(ciphertext) != self.params["ciphertext_size"]:
            raise ValueError("Invalid ciphertext size")
        if len(private_key) != self.params["private_key_size"]:
            raise ValueError("Invalid private key size")
        
        # Return consistent shared secret for simulation
        return hashlib.sha256(ciphertext + private_key).digest()[:self.params["shared_secret_size"]]

class McElieceImplementation:
    """Classic McEliece implementation - Code-based cryptography"""
    
    def __init__(self, parameter_set: str = "mceliece348864"):
        self.parameter_set = parameter_set
        
        # Classic McEliece parameter sets
        self.parameters = {
            "mceliece348864": {
                "m": 12,
                "n": 3488,
                "t": 64,
                "security_level": SecurityLevel.LEVEL_1,
                "public_key_size": 261120,
                "private_key_size": 6492,
                "ciphertext_size": 128,
                "shared_secret_size": 32
            },
            "mceliece460896": {
                "m": 13,
                "n": 4608,
                "t": 96,
                "security_level": SecurityLevel.LEVEL_3,
                "public_key_size": 524160,
                "private_key_size": 13608,
                "ciphertext_size": 188,
                "shared_secret_size": 32
            },
            "mceliece6688128": {
                "m": 13,
                "n": 6688,
                "t": 128,
                "security_level": SecurityLevel.LEVEL_5,
                "public_key_size": 1044992,
                "private_key_size": 13932,
                "ciphertext_size": 240,
                "shared_secret_size": 32
            }
        }
        
        if parameter_set not in self.parameters:
            raise ValueError(f"Unknown McEliece parameter set: {parameter_set}")
        
        self.params = self.parameters[parameter_set]
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate McEliece key pair (simulation)"""
        # McEliece has very large public keys due to the generator matrix
        public_key = secrets.token_bytes(self.params["public_key_size"])
        private_key = secrets.token_bytes(self.params["private_key_size"])
        
        return public_key, private_key
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """McEliece encapsulation (simulation)"""
        if len(public_key) != self.params["public_key_size"]:
            raise ValueError("Invalid public key size")
        
        shared_secret = secrets.token_bytes(self.params["shared_secret_size"])
        ciphertext = secrets.token_bytes(self.params["ciphertext_size"])
        
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """McEliece decapsulation (simulation)"""
        if len(ciphertext) != self.params["ciphertext_size"]:
            raise ValueError("Invalid ciphertext size")
        if len(private_key) != self.params["private_key_size"]:
            raise ValueError("Invalid private key size")
        
        return hashlib.sha256(ciphertext + private_key).digest()[:self.params["shared_secret_size"]]

class RainbowImplementation:
    """Rainbow multivariate signature scheme (Note: Rainbow was broken in 2022)"""
    
    def __init__(self, parameter_set: str = "rainbow-I-classic"):
        self.parameter_set = parameter_set
        print("WARNING: Rainbow was cryptanalyzed and broken in 2022. This is for educational purposes only.")
        
        # Rainbow parameter sets (historical)
        self.parameters = {
            "rainbow-I-classic": {
                "security_level": SecurityLevel.LEVEL_1,
                "field_size": 16,
                "variables": (36, 32, 32),
                "public_key_size": 158312,
                "private_key_size": 103648,
                "signature_size": 66,
                "status": "BROKEN"
            },
            "rainbow-III-classic": {
                "security_level": SecurityLevel.LEVEL_3,
                "field_size": 16,
                "variables": (68, 32, 48),
                "public_key_size": 882080,
                "private_key_size": 626048,
                "signature_size": 164,
                "status": "BROKEN"
            }
        }
        
        if parameter_set not in self.parameters:
            raise ValueError(f"Unknown Rainbow parameter set: {parameter_set}")
        
        self.params = self.parameters[parameter_set]
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate Rainbow key pair (simulation - BROKEN ALGORITHM)"""
        public_key = secrets.token_bytes(self.params["public_key_size"])
        private_key = secrets.token_bytes(self.params["private_key_size"])
        
        return public_key, private_key
    
    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """Rainbow signature (simulation - BROKEN ALGORITHM)"""
        message_hash = hashlib.sha256(message).digest()
        signature_material = private_key + message_hash
        
        # Generate signature of appropriate size
        return hashlib.sha256(signature_material).digest()[:self.params["signature_size"]]
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Rainbow verification (simulation - BROKEN ALGORITHM)"""
        return len(signature) == self.params["signature_size"] and len(public_key) == self.params["public_key_size"]

class GeMSSImplementation:
    """GeMSS multivariate signature scheme"""
    
    def __init__(self, parameter_set: str = "gemss-128"):
        self.parameter_set = parameter_set
        
        # GeMSS parameter sets
        self.parameters = {
            "gemss-128": {
                "security_level": SecurityLevel.LEVEL_1,
                "field_extension": 174,
                "polynomial_degree": 129,
                "public_key_size": 352188,
                "private_key_size": 16,
                "signature_size": 33,
                "hash_function": "SHA3-224"
            },
            "gemss-192": {
                "security_level": SecurityLevel.LEVEL_3,
                "field_extension": 265,
                "polynomial_degree": 193,
                "public_key_size": 1237964,
                "private_key_size": 24,
                "signature_size": 49,
                "hash_function": "SHA3-256"
            },
            "gemss-256": {
                "security_level": SecurityLevel.LEVEL_5,
                "field_extension": 358,
                "polynomial_degree": 257,
                "public_key_size": 3040596,
                "private_key_size": 32,
                "signature_size": 65,
                "hash_function": "SHA3-384"
            }
        }
        
        if parameter_set not in self.parameters:
            raise ValueError(f"Unknown GeMSS parameter set: {parameter_set}")
        
        self.params = self.parameters[parameter_set]
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate GeMSS key pair (simulation)"""
        public_key = secrets.token_bytes(self.params["public_key_size"])
        private_key = secrets.token_bytes(self.params["private_key_size"])
        
        return public_key, private_key
    
    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """GeMSS signature (simulation)"""
        # Use appropriate hash function
        if self.params["hash_function"] == "SHA3-224":
            message_hash = hashlib.sha3_224(message).digest()
        elif self.params["hash_function"] == "SHA3-256":
            message_hash = hashlib.sha3_256(message).digest()
        else:  # SHA3-384
            message_hash = hashlib.sha3_384(message).digest()
        
        signature_material = private_key + message_hash
        return hashlib.sha256(signature_material).digest()[:self.params["signature_size"]]
    
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """GeMSS verification (simulation)"""
        return len(signature) == self.params["signature_size"] and len(public_key) == self.params["public_key_size"]

class ExtendedAlgorithmRegistry:
    """Registry for extended post-quantum algorithms"""
    
    def __init__(self):
        self.algorithms = {}
        self._initialize_algorithms()
    
    def _initialize_algorithms(self):
        """Initialize algorithm registry with all supported algorithms"""
        
        # NTRU variants
        ntru_variants = ["hps2048509", "hps2048677", "hps4096821", "hrss701"]
        for variant in ntru_variants:
            ntru_impl = ExtendedNTRUImplementation(variant)
            self.algorithms[f"NTRU-{variant}"] = AlgorithmParameters(
                name=f"NTRU-{variant}",
                family=PQAlgorithmFamily.LATTICE_BASED,
                security_level=ntru_impl.params["security_level"],
                key_sizes={
                    "public_key": ntru_impl.params["public_key_size"],
                    "private_key": ntru_impl.params["private_key_size"],
                    "ciphertext": ntru_impl.params["ciphertext_size"]
                },
                performance_characteristics={
                    "key_generation": "fast",
                    "encapsulation": "fast",
                    "decapsulation": "fast",
                    "key_sizes": "moderate"
                },
                standardization_status="NIST_Candidate",
                implementation_notes="Lattice-based KEM with good performance characteristics"
            )
        
        # SPHINCS+ variants
        sphincs_variants = [
            "sphincs-sha256-128f-robust", "sphincs-sha256-128s-robust",
            "sphincs-sha256-192f-robust", "sphincs-sha256-256f-robust",
            "sphincs-shake256-128f-robust"
        ]
        for variant in sphincs_variants:
            sphincs_impl = SPHINCSPlusImplementation(variant)
            self.algorithms[f"SPHINCS+-{variant}"] = AlgorithmParameters(
                name=f"SPHINCS+-{variant}",
                family=PQAlgorithmFamily.HASH_BASED,
                security_level=sphincs_impl.params["security_level"],
                key_sizes={
                    "public_key": sphincs_impl.params["public_key_size"],
                    "private_key": sphincs_impl.params["private_key_size"],
                    "signature": sphincs_impl.params["signature_size"]
                },
                performance_characteristics={
                    "key_generation": "fast",
                    "signing": "slow",
                    "verification": "fast",
                    "signature_sizes": "very_large"
                },
                standardization_status="NIST_Standard",
                implementation_notes="Hash-based signature with strong security guarantees but large signatures"
            )
        
        # FrodoKEM variants
        frodo_variants = ["FrodoKEM-640-AES", "FrodoKEM-976-AES", "FrodoKEM-1344-AES"]
        for variant in frodo_variants:
            frodo_impl = FrodoKEMImplementation(variant)
            self.algorithms[variant] = AlgorithmParameters(
                name=variant,
                family=PQAlgorithmFamily.LATTICE_BASED,
                security_level=frodo_impl.params["security_level"],
                key_sizes={
                    "public_key": frodo_impl.params["public_key_size"],
                    "private_key": frodo_impl.params["private_key_size"],
                    "ciphertext": frodo_impl.params["ciphertext_size"]
                },
                performance_characteristics={
                    "key_generation": "moderate",
                    "encapsulation": "moderate",
                    "decapsulation": "moderate",
                    "key_sizes": "large"
                },
                standardization_status="Alternative",
                implementation_notes="Conservative lattice-based approach with larger key sizes"
            )
        
        # Classic McEliece variants
        mceliece_variants = ["mceliece348864", "mceliece460896", "mceliece6688128"]
        for variant in mceliece_variants:
            mceliece_impl = McElieceImplementation(variant)
            self.algorithms[f"Classic-McEliece-{variant}"] = AlgorithmParameters(
                name=f"Classic-McEliece-{variant}",
                family=PQAlgorithmFamily.CODE_BASED,
                security_level=mceliece_impl.params["security_level"],
                key_sizes={
                    "public_key": mceliece_impl.params["public_key_size"],
                    "private_key": mceliece_impl.params["private_key_size"],
                    "ciphertext": mceliece_impl.params["ciphertext_size"]
                },
                performance_characteristics={
                    "key_generation": "slow",
                    "encapsulation": "fast",
                    "decapsulation": "fast",
                    "public_key_sizes": "very_large"
                },
                standardization_status="NIST_Candidate",
                implementation_notes="Code-based KEM with very large public keys but fast operations"
            )
        
        # GeMSS variants
        gemss_variants = ["gemss-128", "gemss-192", "gemss-256"]
        for variant in gemss_variants:
            gemss_impl = GeMSSImplementation(variant)
            self.algorithms[f"GeMSS-{variant}"] = AlgorithmParameters(
                name=f"GeMSS-{variant}",
                family=PQAlgorithmFamily.MULTIVARIATE,
                security_level=gemss_impl.params["security_level"],
                key_sizes={
                    "public_key": gemss_impl.params["public_key_size"],
                    "private_key": gemss_impl.params["private_key_size"],
                    "signature": gemss_impl.params["signature_size"]
                },
                performance_characteristics={
                    "key_generation": "slow",
                    "signing": "moderate",
                    "verification": "fast",
                    "signatures": "small"
                },
                standardization_status="Alternative",
                implementation_notes="Multivariate signature with small signatures but large public keys"
            )
    
    def get_algorithm(self, name: str) -> Optional[AlgorithmParameters]:
        """Get algorithm parameters by name"""
        return self.algorithms.get(name)
    
    def list_algorithms_by_family(self, family: PQAlgorithmFamily) -> List[str]:
        """List all algorithms in a given family"""
        return [name for name, params in self.algorithms.items() 
                if params.family == family]
    
    def list_algorithms_by_security_level(self, level: SecurityLevel) -> List[str]:
        """List all algorithms at a given security level"""
        return [name for name, params in self.algorithms.items() 
                if params.security_level == level]
    
    def get_nist_standards(self) -> List[str]:
        """Get list of NIST standardized algorithms"""
        return [name for name, params in self.algorithms.items() 
                if params.standardization_status == "NIST_Standard"]
    
    def get_nist_candidates(self) -> List[str]:
        """Get list of NIST candidate algorithms"""
        return [name for name, params in self.algorithms.items() 
                if params.standardization_status == "NIST_Candidate"]
    
    def generate_algorithm_comparison(self) -> Dict[str, Any]:
        """Generate comprehensive algorithm comparison"""
        comparison = {
            "by_family": {},
            "by_security_level": {},
            "by_standardization": {},
            "key_size_analysis": {},
            "performance_analysis": {}
        }
        
        # Group by family
        for family in PQAlgorithmFamily:
            comparison["by_family"][family.value] = self.list_algorithms_by_family(family)
        
        # Group by security level
        for level in SecurityLevel:
            comparison["by_security_level"][level.value] = self.list_algorithms_by_security_level(level)
        
        # Group by standardization status
        standardization_groups = {"NIST_Standard": [], "NIST_Candidate": [], "Alternative": []}
        for name, params in self.algorithms.items():
            standardization_groups[params.standardization_status].append(name)
        comparison["by_standardization"] = standardization_groups
        
        # Key size analysis
        key_sizes = {}
        for name, params in self.algorithms.items():
            key_sizes[name] = params.key_sizes
        comparison["key_size_analysis"] = key_sizes
        
        # Performance analysis
        performance = {}
        for name, params in self.algorithms.items():
            performance[name] = params.performance_characteristics
        comparison["performance_analysis"] = performance
        
        return comparison
    
    def recommend_algorithms(self, requirements: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Recommend algorithms based on requirements"""
        recommendations = []
        
        required_security = requirements.get("security_level", SecurityLevel.LEVEL_1)
        max_key_size = requirements.get("max_public_key_size", float('inf'))
        max_signature_size = requirements.get("max_signature_size", float('inf'))
        preferred_families = requirements.get("preferred_families", list(PQAlgorithmFamily))
        standardization_preference = requirements.get("standardization_preference", "any")
        
        for name, params in self.algorithms.items():
            # Check security level
            if params.security_level.value < required_security.value:
                continue
            
            # Check family preference
            if params.family not in preferred_families:
                continue
            
            # Check standardization preference
            if standardization_preference != "any" and params.standardization_status != standardization_preference:
                continue
            
            # Check key size constraints
            if params.key_sizes.get("public_key", 0) > max_key_size:
                continue
            
            if params.key_sizes.get("signature", 0) > max_signature_size:
                continue
            
            # Calculate recommendation score
            score_factors = []
            
            # Prefer NIST standards
            if params.standardization_status == "NIST_Standard":
                score_factors.append("NIST_Standard")
            elif params.standardization_status == "NIST_Candidate":
                score_factors.append("NIST_Candidate")
            
            # Consider performance characteristics
            perf = params.performance_characteristics
            if perf.get("key_generation") == "fast":
                score_factors.append("fast_keygen")
            if perf.get("signing") == "fast" or perf.get("encapsulation") == "fast":
                score_factors.append("fast_crypto_ops")
            
            # Prefer smaller key sizes
            public_key_size = params.key_sizes.get("public_key", 0)
            if public_key_size < 10000:
                score_factors.append("compact_keys")
            
            reason = f"Security Level {params.security_level.value}, {params.family.value}, " + ", ".join(score_factors)
            recommendations.append((name, reason))
        
        # Sort by preference (NIST standards first, then candidates, then alternatives)
        def sort_key(item):
            name, reason = item
            params = self.algorithms[name]
            if params.standardization_status == "NIST_Standard":
                return (0, name)
            elif params.standardization_status == "NIST_Candidate":
                return (1, name)
            else:
                return (2, name)
        
        recommendations.sort(key=sort_key)
        return recommendations

class AlgorithmBenchmarkSuite:
    """Benchmark suite for extended post-quantum algorithms"""
    
    def __init__(self):
        self.registry = ExtendedAlgorithmRegistry()
        self.benchmark_results = {}
    
    def benchmark_kem_algorithms(self, iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Benchmark KEM algorithms"""
        print("Benchmarking KEM Algorithms...")
        results = {}
        
        kem_algorithms = [
            ("NTRU-hps2048509", ExtendedNTRUImplementation("hps2048509")),
            ("NTRU-hps2048677", ExtendedNTRUImplementation("hps2048677")),
            ("FrodoKEM-640-AES", FrodoKEMImplementation("FrodoKEM-640-AES")),
            ("Classic-McEliece-348864", McElieceImplementation("mceliece348864"))
        ]
        
        for name, implementation in kem_algorithms:
            print(f"  Testing {name}...")
            
            # Key generation benchmark
            keygen_times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                public_key, private_key = implementation.generate_keypair()
                keygen_times.append(time.perf_counter() - start_time)
            
            # Encapsulation benchmark
            encap_times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                ciphertext, shared_secret = implementation.encapsulate(public_key)
                encap_times.append(time.perf_counter() - start_time)
            
            # Decapsulation benchmark
            decap_times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                recovered_secret = implementation.decapsulate(ciphertext, private_key)
                decap_times.append(time.perf_counter() - start_time)
            
            results[name] = {
                "keygen_avg_ms": sum(keygen_times) / len(keygen_times) * 1000,
                "encap_avg_ms": sum(encap_times) / len(encap_times) * 1000,
                "decap_avg_ms": sum(decap_times) / len(decap_times) * 1000,
                "public_key_size": len(public_key),
                "private_key_size": len(private_key),
                "ciphertext_size": len(ciphertext)
            }
        
        return results
    
    def benchmark_signature_algorithms(self, iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Benchmark signature algorithms"""
        print("Benchmarking Signature Algorithms...")
        results = {}
        
        test_message = b"This is a test message for benchmarking post-quantum signature algorithms"
        
        signature_algorithms = [
            ("SPHINCS+-sha256-128f", SPHINCSPlusImplementation("sphincs-sha256-128f-robust")),
            ("SPHINCS+-sha256-128s", SPHINCSPlusImplementation("sphincs-sha256-128s-robust")),
            ("GeMSS-128", GeMSSImplementation("gemss-128")),
        ]
        
        for name, implementation in signature_algorithms:
            print(f"  Testing {name}...")
            
            # Key generation benchmark
            keygen_times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                public_key, private_key = implementation.generate_keypair()
                keygen_times.append(time.perf_counter() - start_time)
            
            # Signing benchmark
            sign_times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                signature = implementation.sign(test_message, private_key)
                sign_times.append(time.perf_counter() - start_time)
            
            # Verification benchmark
            verify_times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                is_valid = implementation.verify(test_message, signature, public_key)
                verify_times.append(time.perf_counter() - start_time)
            
            results[name] = {
                "keygen_avg_ms": sum(keygen_times) / len(keygen_times) * 1000,
                "sign_avg_ms": sum(sign_times) / len(sign_times) * 1000,
                "verify_avg_ms": sum(verify_times) / len(verify_times) * 1000,
                "public_key_size": len(public_key),
                "private_key_size": len(private_key),
                "signature_size": len(signature),
                "verification_success": is_valid
            }
        
        return results
    
    def generate_benchmark_report(self, output_file: str = "extended_pq_benchmark.json"):
        """Generate comprehensive benchmark report"""
        print("Generating comprehensive benchmark report...")
        
        # Run benchmarks
        kem_results = self.benchmark_kem_algorithms(50)  # Reduced iterations for demo
        signature_results = self.benchmark_signature_algorithms(50)
        
        # Get algorithm comparison
        comparison = self.registry.generate_algorithm_comparison()
        
        report = {
            "benchmark_timestamp": datetime.now().isoformat(),
            "benchmark_iterations": 50,
            "kem_benchmark_results": kem_results,
            "signature_benchmark_results": signature_results,
            "algorithm_comparison": comparison,
            "summary": self._generate_benchmark_summary(kem_results, signature_results),
            "recommendations": self._generate_algorithm_recommendations()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Benchmark report saved to: {output_file}")
        return report
    
    def _generate_benchmark_summary(self, kem_results: Dict, signature_results: Dict) -> Dict[str, Any]:
        """Generate benchmark summary"""
        summary = {
            "fastest_kem_keygen": None,
            "fastest_kem_encap": None,
            "smallest_kem_keys": None,
            "fastest_signature_keygen": None,
            "fastest_signing": None,
            "smallest_signatures": None
        }
        
        # Find fastest KEM operations
        if kem_results:
            fastest_keygen = min(kem_results.items(), key=lambda x: x[1]["keygen_avg_ms"])
            fastest_encap = min(kem_results.items(), key=lambda x: x[1]["encap_avg_ms"])
            smallest_keys = min(kem_results.items(), key=lambda x: x[1]["public_key_size"])
            
            summary["fastest_kem_keygen"] = {"algorithm": fastest_keygen[0], "time_ms": fastest_keygen[1]["keygen_avg_ms"]}
            summary["fastest_kem_encap"] = {"algorithm": fastest_encap[0], "time_ms": fastest_encap[1]["encap_avg_ms"]}
            summary["smallest_kem_keys"] = {"algorithm": smallest_keys[0], "size_bytes": smallest_keys[1]["public_key_size"]}
        
        # Find fastest signature operations
        if signature_results:
            fastest_keygen = min(signature_results.items(), key=lambda x: x[1]["keygen_avg_ms"])
            fastest_sign = min(signature_results.items(), key=lambda x: x[1]["sign_avg_ms"])
            smallest_sigs = min(signature_results.items(), key=lambda x: x[1]["signature_size"])
            
            summary["fastest_signature_keygen"] = {"algorithm": fastest_keygen[0], "time_ms": fastest_keygen[1]["keygen_avg_ms"]}
            summary["fastest_signing"] = {"algorithm": fastest_sign[0], "time_ms": fastest_sign[1]["sign_avg_ms"]}
            summary["smallest_signatures"] = {"algorithm": smallest_sigs[0], "size_bytes": smallest_sigs[1]["signature_size"]}
        
        return summary
    
    def _generate_algorithm_recommendations(self) -> Dict[str, List[str]]:
        """Generate algorithm recommendations for different use cases"""
        recommendations = {}
        
        # High-performance applications
        high_perf_reqs = {
            "security_level": SecurityLevel.LEVEL_1,
            "max_public_key_size": 50000,
            "standardization_preference": "NIST_Standard"
        }
        recommendations["high_performance"] = [
            rec[0] for rec in self.registry.recommend_algorithms(high_perf_reqs)[:3]
        ]
        
        # High-security applications
        high_sec_reqs = {
            "security_level": SecurityLevel.LEVEL_5,
            "standardization_preference": "NIST_Standard"
        }
        recommendations["high_security"] = [
            rec[0] for rec in self.registry.recommend_algorithms(high_sec_reqs)[:3]
        ]
        
        # Constrained environments
        constrained_reqs = {
            "security_level": SecurityLevel.LEVEL_1,
            "max_public_key_size": 2000,
            "max_signature_size": 1000
        }
        recommendations["constrained_environment"] = [
            rec[0] for rec in self.registry.recommend_algorithms(constrained_reqs)[:3]
        ]
        
        return recommendations

# Example usage and demonstration
if __name__ == "__main__":
    print("=== Extended Post-Quantum Algorithm Support ===\n")
    
    # Initialize registry and benchmark suite
    registry = ExtendedAlgorithmRegistry()
    benchmark_suite = AlgorithmBenchmarkSuite()
    
    # Demo 1: Algorithm Registry Overview
    print("1. Algorithm Registry Overview")
    print("-" * 50)
    
    print(f"Total algorithms registered: {len(registry.algorithms)}")
    
    for family in PQAlgorithmFamily:
        algorithms = registry.list_algorithms_by_family(family)
        if algorithms:
            print(f"\n{family.value.title()} algorithms ({len(algorithms)}):")
            for alg in algorithms[:3]:  # Show first 3
                params = registry.get_algorithm(alg)
                print(f"  • {alg} (Security Level {params.security_level.value})")
    
    # Demo 2: NIST Standards vs Candidates
    print("\n\n2. NIST Standardization Status")
    print("-" * 50)
    
    nist_standards = registry.get_nist_standards()
    nist_candidates = registry.get_nist_candidates()
    
    print(f"NIST Standardized Algorithms ({len(nist_standards)}):")
    for alg in nist_standards:
        print(f"  ✓ {alg}")
    
    print(f"\nNIST Candidate Algorithms ({len(nist_candidates)}):")
    for alg in nist_candidates[:5]:  # Show first 5
        print(f"  • {alg}")
    
    # Demo 3: Key Size Comparison
    print("\n\n3. Key Size Analysis")
    print("-" * 50)
    
    print(f"{'Algorithm':<30} {'Public Key':<12} {'Private Key':<12} {'Signature/CT':<12}")
    print("-" * 70)
    
    sample_algorithms = [
        "NTRU-hps2048509",
        "SPHINCS+-sphincs-sha256-128f-robust", 
        "FrodoKEM-640-AES",
        "Classic-McEliece-mceliece348864",
        "GeMSS-gemss-128"
    ]
    
    for alg_name in sample_algorithms:
        if alg_name in registry.algorithms:
            params = registry.get_algorithm(alg_name)
            pub_size = params.key_sizes.get("public_key", 0)
            priv_size = params.key_sizes.get("private_key", 0)
            sig_size = params.key_sizes.get("signature", params.key_sizes.get("ciphertext", 0))
            
            print(f"{alg_name:<30} {pub_size:<12} {priv_size:<12} {sig_size:<12}")
    
    # Demo 4: Algorithm Recommendations
    print("\n\n4. Algorithm Recommendations")
    print("-" * 50)
    
    use_cases = [
        {
            "name": "High Performance Web Server",
            "requirements": {
                "security_level": SecurityLevel.LEVEL_1,
                "max_public_key_size": 10000,
                "standardization_preference": "NIST_Standard"
            }
        },
        {
            "name": "Government System",
            "requirements": {
                "security_level": SecurityLevel.LEVEL_5,
                "standardization_preference": "NIST_Standard"
            }
        },
        {
            "name": "IoT Device",
            "requirements": {
                "security_level": SecurityLevel.LEVEL_1,
                "max_public_key_size": 1000,
                "max_signature_size": 500
            }
        }
    ]
    
    for use_case in use_cases:
        print(f"\n{use_case['name']}:")
        recommendations = registry.recommend_algorithms(use_case['requirements'])
        
        for i, (alg_name, reason) in enumerate(recommendations[:3]):
            print(f"  {i+1}. {alg_name}")
            print(f"     Reason: {reason}")
    
    # Demo 5: Performance Benchmarking (Sample)
    print("\n\n5. Performance Benchmarking Sample")
    print("-" * 50)
    
    print("Running sample benchmarks...")
    
    # Quick NTRU benchmark
    ntru = ExtendedNTRUImplementation("hps2048509")
    
    start_time = time.perf_counter()
    pub_key, priv_key = ntru.generate_keypair()
    keygen_time = time.perf_counter() - start_time
    
    start_time = time.perf_counter()
    ciphertext, secret = ntru.encapsulate(pub_key)
    encap_time = time.perf_counter() - start_time
    
    print(f"\nNTRU-HPS-2048-509 Sample Results:")
    print(f"  Key Generation: {keygen_time*1000:.2f} ms")
    print(f"  Encapsulation:  {encap_time*1000:.2f} ms")
    print(f"  Public Key:     {len(pub_key)} bytes")
    print(f"  Ciphertext:     {len(ciphertext)} bytes")
    
    # Quick SPHINCS+ benchmark
    sphincs = SPHINCSPlusImplementation("sphincs-sha256-128f-robust")
    
    start_time = time.perf_counter()
    pub_key, priv_key = sphincs.generate_keypair()
    keygen_time = time.perf_counter() - start_time
    
    test_msg = b"Test message for SPHINCS+"
    start_time = time.perf_counter()
    signature = sphincs.sign(test_msg, priv_key)
    sign_time = time.perf_counter() - start_time
    
    print(f"\nSPHINCS+-SHA256-128f Sample Results:")
    print(f"  Key Generation: {keygen_time*1000:.2f} ms")
    print(f"  Signing:        {sign_time*1000:.2f} ms")
    print(f"  Public Key:     {len(pub_key)} bytes")
    print(f"  Signature:      {len(signature)} bytes")
    
    # Demo 6: Algorithm Comparison Report
    print("\n\n6. Generating Algorithm Comparison")
    print("-" * 50)
    
    comparison = registry.generate_algorithm_comparison()
    
    print("Algorithm Families:")
    for family, algorithms in comparison["by_family"].items():
        if algorithms:
            print(f"  {family.title()}: {len(algorithms)} algorithms")
    
    print(f"\nSecurity Level Distribution:")
    for level, algorithms in comparison["by_security_level"].items():
        if algorithms:
            print(f"  Level {level}: {len(algorithms)} algorithms")
    
    print(f"\nStandardization Status:")
    for status, algorithms in comparison["by_standardization"].items():
        print(f"  {status.replace('_', ' ')}: {len(algorithms)} algorithms")
    
    print("\n=== Extended Algorithm Analysis Complete ===")
    print("This module provides comprehensive support for:")
    print("• NTRU lattice-based KEM variants")
    print("• SPHINCS+ hash-based signatures")
    print("• FrodoKEM conservative lattice approach") 
    print("• Classic McEliece code-based cryptography")
    print("• GeMSS multivariate signatures")
    print("• Algorithm comparison and recommendation system")
    print("• Performance benchmarking framework")
    
    print("\nNote: All implementations are simulations for demonstration.")
    print("Production use requires proper cryptographic libraries.")
