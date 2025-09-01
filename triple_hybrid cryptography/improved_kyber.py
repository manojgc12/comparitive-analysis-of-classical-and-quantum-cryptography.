import time
import hashlib
import secrets
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, List, Any
import json
from datetime import datetime
from oqs import KeyEncapsulation

@dataclass
class KeyMetadata:
    """Metadata for generated keys"""
    algorithm: str
    generation_time: float
    key_size_public: int
    key_size_private: int
    timestamp: str
    security_level: int
    fingerprint: str

class ImprovedKyberKEM:
    """
    Enhanced Kyber Key Encapsulation Mechanism with optimizations and additional features
    """
    
    # Security levels for different Kyber variants
    SECURITY_LEVELS = {
        "Kyber512": 128,   # AES-128 equivalent
        "Kyber768": 192,   # AES-192 equivalent
        "Kyber1024": 256   # AES-256 equivalent
    }
    
    def __init__(self, algorithm: str = "Kyber768", enable_caching: bool = True):
        """
        Initialize improved Kyber KEM
        
        Args:
            algorithm: Kyber variant to use
            enable_caching: Enable key caching for performance
        """
        self.algorithm = algorithm
        self.enable_caching = enable_caching
        self.key_cache: Dict[str, Tuple[bytes, bytes, KeyMetadata]] = {}
        self.kem = None
        self._lock = threading.Lock()
        
        # Validate algorithm
        if algorithm not in self.SECURITY_LEVELS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        print(f"Initialized ImprovedKyberKEM with {algorithm}")
        print(f"Security level: {self.SECURITY_LEVELS[algorithm]} bits")
    
    def _get_fingerprint(self, public_key: bytes) -> str:
        """Generate fingerprint for a public key"""
        return hashlib.sha256(public_key).hexdigest()[:16].upper()
    
    def _create_key_metadata(self, public_key: bytes, private_key: bytes, 
                           generation_time: float) -> KeyMetadata:
        """Create metadata for generated keys"""
        return KeyMetadata(
            algorithm=self.algorithm,
            generation_time=generation_time,
            key_size_public=len(public_key),
            key_size_private=len(private_key),
            timestamp=datetime.now().isoformat(),
            security_level=self.SECURITY_LEVELS[self.algorithm],
            fingerprint=self._get_fingerprint(public_key)
        )
    
    def generate_keypair_optimized(self, cache_key: Optional[str] = None) -> Tuple[bytes, bytes, KeyMetadata]:
        """
        Generate optimized keypair with metadata and optional caching
        
        Args:
            cache_key: Optional key for caching the generated keypair
            
        Returns:
            Tuple of (public_key, private_key, metadata)
        """
        # Check cache first
        if self.enable_caching and cache_key and cache_key in self.key_cache:
            print(f"Using cached keypair for: {cache_key}")
            return self.key_cache[cache_key]
        
        with self._lock:
            # Create KEM instance
            kem = KeyEncapsulation(self.algorithm)
            
            # Measure generation time
            start_time = time.perf_counter()
            public_key, private_key = kem.generate_keypair()
            end_time = time.perf_counter()
            
            generation_time = (end_time - start_time) * 1000  # milliseconds
            
            # Create metadata
            metadata = self._create_key_metadata(public_key, private_key, generation_time)
            
            # Cache if requested
            if self.enable_caching and cache_key:
                self.key_cache[cache_key] = (public_key, private_key, metadata)
                print(f"Cached keypair for: {cache_key}")
            
            return public_key, private_key, metadata
    
    def batch_generate_keypairs(self, count: int, max_workers: int = 4) -> List[Tuple[bytes, bytes, KeyMetadata]]:
        """
        Generate multiple keypairs in parallel for improved performance
        
        Args:
            count: Number of keypairs to generate
            max_workers: Maximum number of worker threads
            
        Returns:
            List of keypairs with metadata
        """
        print(f"Generating {count} keypairs using {max_workers} workers...")
        
        keypairs = []
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks
            futures = []
            for i in range(count):
                future = executor.submit(self.generate_keypair_optimized, f"batch_{i}")
                futures.append(future)
            
            # Collect results
            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    keypairs.append(result)
                    if (i + 1) % 10 == 0:
                        print(f"Generated {i + 1}/{count} keypairs...")
                except Exception as e:
                    print(f"Error generating keypair {i}: {e}")
        
        total_time = (time.perf_counter() - start_time) * 1000
        avg_time = total_time / count if count > 0 else 0
        
        print(f"Batch generation completed:")
        print(f"Total time: {total_time:.2f} ms")
        print(f"Average time per keypair: {avg_time:.2f} ms")
        
        return keypairs
    
    def encapsulate_enhanced(self, public_key: bytes) -> Tuple[bytes, bytes, Dict[str, Any]]:
        """
        Enhanced encapsulation with timing and metadata
        
        Args:
            public_key: Public key for encapsulation
            
        Returns:
            Tuple of (ciphertext, shared_secret, metadata)
        """
        kem = KeyEncapsulation(self.algorithm)
        
        start_time = time.perf_counter()
        ciphertext, shared_secret = kem.encaps(public_key)
        end_time = time.perf_counter()
        
        encaps_time = (end_time - start_time) * 1000
        
        metadata = {
            'encapsulation_time_ms': encaps_time,
            'ciphertext_size': len(ciphertext),
            'shared_secret_size': len(shared_secret),
            'timestamp': datetime.now().isoformat(),
            'public_key_fingerprint': self._get_fingerprint(public_key)
        }
        
        return ciphertext, shared_secret, metadata
    
    def decapsulate_enhanced(self, private_key: bytes, ciphertext: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """
        Enhanced decapsulation with timing and metadata
        
        Args:
            private_key: Private key for decapsulation
            ciphertext: Ciphertext to decapsulate
            
        Returns:
            Tuple of (shared_secret, metadata)
        """
        kem = KeyEncapsulation(self.algorithm)
        
        start_time = time.perf_counter()
        shared_secret = kem.decaps(private_key, ciphertext)
        end_time = time.perf_counter()
        
        decaps_time = (end_time - start_time) * 1000
        
        metadata = {
            'decapsulation_time_ms': decaps_time,
            'shared_secret_size': len(shared_secret),
            'timestamp': datetime.now().isoformat()
        }
        
        return shared_secret, metadata
    
    def benchmark_performance(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Comprehensive performance benchmark
        
        Args:
            iterations: Number of iterations for benchmarking
            
        Returns:
            Dictionary containing benchmark results
        """
        print(f"Running performance benchmark with {iterations} iterations...")
        
        keygen_times = []
        encaps_times = []
        decaps_times = []
        
        for i in range(iterations):
            # Key generation
            start = time.perf_counter()
            public_key, private_key, _ = self.generate_keypair_optimized()
            keygen_time = (time.perf_counter() - start) * 1000
            keygen_times.append(keygen_time)
            
            # Encapsulation
            start = time.perf_counter()
            ciphertext, shared_secret1, _ = self.encapsulate_enhanced(public_key)
            encaps_time = (time.perf_counter() - start) * 1000
            encaps_times.append(encaps_time)
            
            # Decapsulation
            start = time.perf_counter()
            shared_secret2, _ = self.decapsulate_enhanced(private_key, ciphertext)
            decaps_time = (time.perf_counter() - start) * 1000
            decaps_times.append(decaps_time)
            
            # Verify correctness
            assert shared_secret1 == shared_secret2, f"Shared secrets don't match at iteration {i}"
            
            if (i + 1) % 20 == 0:
                print(f"Completed {i + 1}/{iterations} benchmark iterations...")
        
        # Calculate statistics
        def calc_stats(times):
            return {
                'mean': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'std_dev': (sum((t - sum(times)/len(times))**2 for t in times) / len(times))**0.5
            }
        
        results = {
            'algorithm': self.algorithm,
            'iterations': iterations,
            'keygen_stats': calc_stats(keygen_times),
            'encaps_stats': calc_stats(encaps_times),
            'decaps_stats': calc_stats(decaps_times),
            'total_time_ms': sum(keygen_times) + sum(encaps_times) + sum(decaps_times)
        }
        
        return results
    
    def save_keys_to_file(self, public_key: bytes, private_key: bytes, 
                         metadata: KeyMetadata, filename: str):
        """
        Save keys and metadata to file in JSON format
        
        Args:
            public_key: Public key bytes
            private_key: Private key bytes
            metadata: Key metadata
            filename: Output filename
        """
        import base64
        
        data = {
            'public_key': base64.b64encode(public_key).decode('utf-8'),
            'private_key': base64.b64encode(private_key).decode('utf-8'),
            'metadata': {
                'algorithm': metadata.algorithm,
                'generation_time': metadata.generation_time,
                'key_size_public': metadata.key_size_public,
                'key_size_private': metadata.key_size_private,
                'timestamp': metadata.timestamp,
                'security_level': metadata.security_level,
                'fingerprint': metadata.fingerprint
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Keys saved to: {filename}")
    
    def load_keys_from_file(self, filename: str) -> Tuple[bytes, bytes, KeyMetadata]:
        """
        Load keys and metadata from file
        
        Args:
            filename: Input filename
            
        Returns:
            Tuple of (public_key, private_key, metadata)
        """
        import base64
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        public_key = base64.b64decode(data['public_key'])
        private_key = base64.b64decode(data['private_key'])
        
        metadata = KeyMetadata(**data['metadata'])
        
        print(f"Keys loaded from: {filename}")
        return public_key, private_key, metadata
    
    def clear_cache(self):
        """Clear the key cache"""
        with self._lock:
            self.key_cache.clear()
            print("Key cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state"""
        return {
            'cache_enabled': self.enable_caching,
            'cached_keypairs': len(self.key_cache),
            'cache_keys': list(self.key_cache.keys()) if self.key_cache else []
        }

def demo_improved_kyber():
    """Demonstration of the improved Kyber implementation"""
    print("IMPROVED KYBER ALGORITHM DEMONSTRATION")
    print("=" * 60)
    
    try:
        # Test all variants
        for variant in ["Kyber512", "Kyber768", "Kyber1024"]:
            print(f"\n--- Testing {variant} ---")
            
            kem = ImprovedKyberKEM(variant, enable_caching=True)
            
            # Single keypair generation
            public_key, private_key, metadata = kem.generate_keypair_optimized("demo_key")
            
            print(f"Generated keypair:")
            print(f"  Algorithm: {metadata.algorithm}")
            print(f"  Generation time: {metadata.generation_time:.4f} ms")
            print(f"  Public key size: {metadata.key_size_public} bytes")
            print(f"  Private key size: {metadata.key_size_private} bytes")
            print(f"  Security level: {metadata.security_level} bits")
            print(f"  Fingerprint: {metadata.fingerprint}")
            
            # Test encapsulation/decapsulation
            ciphertext, shared_secret1, enc_meta = kem.encapsulate_enhanced(public_key)
            shared_secret2, dec_meta = kem.decapsulate_enhanced(private_key, ciphertext)
            
            print(f"  Encapsulation time: {enc_meta['encapsulation_time_ms']:.4f} ms")
            print(f"  Decapsulation time: {dec_meta['decapsulation_time_ms']:.4f} ms")
            print(f"  Shared secrets match: {shared_secret1 == shared_secret2}")
            
            # Save to file
            filename = f"kyber_{variant.lower()}_keys.json"
            kem.save_keys_to_file(public_key, private_key, metadata, filename)
            
            time.sleep(0.5)
        
        # Batch generation test
        print(f"\n--- Batch Generation Test ---")
        kem = ImprovedKyberKEM("Kyber768")
        batch_keys = kem.batch_generate_keypairs(20, max_workers=4)
        print(f"Successfully generated {len(batch_keys)} keypairs in batch")
        
        # Performance benchmark
        print(f"\n--- Performance Benchmark ---")
        benchmark_results = kem.benchmark_performance(50)
        
        print(f"Benchmark Results for {benchmark_results['algorithm']}:")
        print(f"  Key Generation - Avg: {benchmark_results['keygen_stats']['mean']:.4f} ms")
        print(f"  Encapsulation - Avg: {benchmark_results['encaps_stats']['mean']:.4f} ms")
        print(f"  Decapsulation - Avg: {benchmark_results['decaps_stats']['mean']:.4f} ms")
        
    except ImportError:
        print("Error: 'oqs' library not found!")
        print("Please install it using: pip install python-oqs")
    except Exception as e:
        print(f"Error in demonstration: {e}")

if __name__ == "__main__":
    demo_improved_kyber()
