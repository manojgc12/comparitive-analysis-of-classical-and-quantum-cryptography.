"""
Performance Benchmarking System
Comprehensive benchmarking for classical, hybrid, and post-quantum cryptographic operations
"""

import time
import statistics
import threading
import multiprocessing
import psutil
import gc
import json
import csv
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import secrets
import sys
import os

# Import our crypto modules
from hybrid_tls import HybridTLSHandshake, KeyExchangeType, CryptoAlgorithm
from quantum_signatures import HybridSignatureSystem, SignatureAlgorithm
from client_server_apps import QuantumSafeServer, QuantumSafeClient, ServerConfig, ClientConfig, ConnectionMode

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class BenchmarkType(Enum):
    """Types of benchmarks to run"""
    KEY_GENERATION = "key_generation"
    SIGNING = "signing"
    VERIFICATION = "verification"
    HANDSHAKE = "handshake"
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    FULL_PROTOCOL = "full_protocol"

class MetricType(Enum):
    """Performance metrics to measure"""
    TIME = "time_ms"
    MEMORY = "memory_mb"
    CPU_USAGE = "cpu_percent"
    KEY_SIZE = "key_size_bytes"
    SIGNATURE_SIZE = "signature_size_bytes"
    THROUGHPUT = "throughput_ops_per_sec"
    LATENCY = "latency_ms"

@dataclass
class BenchmarkResult:
    """Individual benchmark result"""
    algorithm: str
    benchmark_type: BenchmarkType
    iterations: int
    measurements: List[float]
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_95: float
    percentile_99: float
    metric_type: MetricType
    metadata: Dict[str, Any]

@dataclass
class SystemInfo:
    """System information for benchmark context"""
    cpu_count: int
    cpu_freq: float
    memory_total: float
    python_version: str
    platform: str
    timestamp: datetime

class PerformanceMonitor:
    """Monitor system performance during benchmarks"""
    
    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.monitoring = False
        self.cpu_readings = []
        self.memory_readings = []
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.cpu_readings.clear()
        self.memory_readings.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return statistics"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        if self.cpu_readings and self.memory_readings:
            return {
                "avg_cpu_percent": statistics.mean(self.cpu_readings),
                "max_cpu_percent": max(self.cpu_readings),
                "avg_memory_mb": statistics.mean(self.memory_readings),
                "max_memory_mb": max(self.memory_readings)
            }
        else:
            return {}
    
    def _monitor_loop(self):
        """Monitoring loop"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                self.cpu_readings.append(cpu_percent)
                self.memory_readings.append(memory_mb)
                
                time.sleep(self.interval)
            except:
                break

class CryptographicBenchmark:
    """Comprehensive cryptographic performance benchmark suite"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
        self.signature_system = HybridSignatureSystem()
        self.monitor = PerformanceMonitor()
        self.system_info = self._get_system_info()
        self.results: List[BenchmarkResult] = []
        
        # Test data sizes
        self.test_data_sizes = [
            ("small", 64),      # 64 bytes
            ("medium", 1024),   # 1 KB
            ("large", 10240),   # 10 KB
            ("xlarge", 102400), # 100 KB
        ]
        
        print(f"Benchmark initialized with {iterations} iterations per test")
        print(f"System: {self.system_info.cpu_count} CPUs, "
              f"{self.system_info.memory_total:.1f} GB RAM")
    
    def _get_system_info(self) -> SystemInfo:
        """Get system information"""
        return SystemInfo(
            cpu_count=multiprocessing.cpu_count(),
            cpu_freq=psutil.cpu_freq().current if psutil.cpu_freq() else 0.0,
            memory_total=psutil.virtual_memory().total / (1024**3),
            python_version=sys.version,
            platform=sys.platform,
            timestamp=datetime.now()
        )
    
    def _measure_operation(self, operation: Callable, metric_type: MetricType = MetricType.TIME) -> List[float]:
        """Measure an operation multiple times"""
        measurements = []
        
        # Warm up
        for _ in range(min(10, self.iterations // 10)):
            try:
                operation()
            except:
                pass
        
        # Force garbage collection
        gc.collect()
        
        # Actual measurements
        for i in range(self.iterations):
            if metric_type == MetricType.TIME:
                start_time = time.perf_counter()
                try:
                    result = operation()
                    end_time = time.perf_counter()
                    measurements.append((end_time - start_time) * 1000)  # Convert to ms
                except Exception as e:
                    # Skip failed operations but log them
                    measurements.append(float('inf'))
            
            elif metric_type == MetricType.MEMORY:
                process = psutil.Process()
                before_memory = process.memory_info().rss
                try:
                    result = operation()
                    after_memory = process.memory_info().rss
                    measurements.append((after_memory - before_memory) / (1024 * 1024))  # MB
                except:
                    measurements.append(0.0)
        
        # Filter out failed measurements
        measurements = [m for m in measurements if m != float('inf')]
        return measurements
    
    def _create_benchmark_result(self, algorithm: str, benchmark_type: BenchmarkType, 
                                measurements: List[float], metric_type: MetricType,
                                metadata: Dict[str, Any] = None) -> BenchmarkResult:
        """Create a benchmark result from measurements"""
        if not measurements:
            measurements = [0.0]
        
        return BenchmarkResult(
            algorithm=algorithm,
            benchmark_type=benchmark_type,
            iterations=len(measurements),
            measurements=measurements,
            mean=statistics.mean(measurements),
            median=statistics.median(measurements),
            std_dev=statistics.stdev(measurements) if len(measurements) > 1 else 0.0,
            min_value=min(measurements),
            max_value=max(measurements),
            percentile_95=np.percentile(measurements, 95) if measurements else 0.0,
            percentile_99=np.percentile(measurements, 99) if measurements else 0.0,
            metric_type=metric_type,
            metadata=metadata or {}
        )
    
    def benchmark_key_generation(self) -> List[BenchmarkResult]:
        """Benchmark key generation for all algorithms"""
        print("\n--- Benchmarking Key Generation ---")
        results = []
        
        # Classical signature algorithms
        classical_sig_algs = [
            SignatureAlgorithm.RSA_PSS_2048,
            SignatureAlgorithm.RSA_PSS_3072,
            SignatureAlgorithm.ECDSA_P256,
            SignatureAlgorithm.ECDSA_P384,
            SignatureAlgorithm.ED25519
        ]
        
        # Post-quantum signature algorithms
        pq_sig_algs = [
            SignatureAlgorithm.DILITHIUM2,
            SignatureAlgorithm.DILITHIUM3,
            SignatureAlgorithm.DILITHIUM5,
            SignatureAlgorithm.FALCON512,
            SignatureAlgorithm.FALCON1024
        ]
        
        # Classical key exchange algorithms
        classical_ke_algs = [
            CryptoAlgorithm.X25519,
            CryptoAlgorithm.X448,
            CryptoAlgorithm.ECDH_P256,
            CryptoAlgorithm.ECDH_P384
        ]
        
        # Post-quantum key exchange algorithms
        pq_ke_algs = [
            CryptoAlgorithm.KYBER512,
            CryptoAlgorithm.KYBER768,
            CryptoAlgorithm.KYBER1024,
            CryptoAlgorithm.NTRU_HPS2048509,
            CryptoAlgorithm.NTRU_HPS2048677
        ]
        
        all_algorithms = [
            ("Classical Signatures", classical_sig_algs, "signature"),
            ("PQ Signatures", pq_sig_algs, "signature"),
            ("Classical Key Exchange", classical_ke_algs, "key_exchange"),
            ("PQ Key Exchange", pq_ke_algs, "key_exchange")
        ]
        
        for category, algorithms, alg_type in all_algorithms:
            print(f"\n{category}:")
            
            for algorithm in algorithms:
                print(f"  Testing {algorithm.value}...", end=" ")
                
                try:
                    if alg_type == "signature":
                        def key_gen():
                            return self.signature_system.create_keypair(algorithm)
                    else:  # key_exchange
                        from hybrid_tls import ClassicalKEM, QuantumSafeKEM
                        if algorithm.value.startswith(("Kyber", "NTRU", "LightSaber", "Saber", "FireSaber")):
                            kem = QuantumSafeKEM(algorithm)
                        else:
                            kem = ClassicalKEM(algorithm)
                        
                        def key_gen():
                            return kem.generate_keypair()
                    
                    # Time measurements
                    time_measurements = self._measure_operation(key_gen, MetricType.TIME)
                    
                    # Memory measurements (smaller sample for memory)
                    memory_measurements = self._measure_operation(
                        key_gen, MetricType.MEMORY
                    ) if self.iterations >= 100 else []
                    
                    # Get key sizes
                    sample_keypair = key_gen()
                    if hasattr(sample_keypair, 'key_size_public'):
                        key_sizes = {
                            "public_key_size": sample_keypair.key_size_public,
                            "private_key_size": sample_keypair.key_size_private
                        }
                    else:
                        key_sizes = {
                            "public_key_size": sample_keypair.key_size,
                            "private_key_size": len(sample_keypair.private_key) if hasattr(sample_keypair, 'private_key') else 0
                        }
                    
                    # Create results
                    time_result = self._create_benchmark_result(
                        algorithm.value, BenchmarkType.KEY_GENERATION,
                        time_measurements, MetricType.TIME, key_sizes
                    )
                    results.append(time_result)
                    
                    if memory_measurements:
                        memory_result = self._create_benchmark_result(
                            algorithm.value, BenchmarkType.KEY_GENERATION,
                            memory_measurements, MetricType.MEMORY, key_sizes
                        )
                        results.append(memory_result)
                    
                    print(f"✓ {time_result.mean:.2f}ms avg")
                
                except Exception as e:
                    print(f"✗ Error: {e}")
        
        return results
    
    def benchmark_signing_verification(self) -> List[BenchmarkResult]:
        """Benchmark signing and verification operations"""
        print("\n--- Benchmarking Signing & Verification ---")
        results = []
        
        signature_algorithms = [
            SignatureAlgorithm.RSA_PSS_2048,
            SignatureAlgorithm.ECDSA_P256,
            SignatureAlgorithm.ED25519,
            SignatureAlgorithm.DILITHIUM2,
            SignatureAlgorithm.DILITHIUM3,
            SignatureAlgorithm.FALCON512
        ]
        
        for data_name, data_size in self.test_data_sizes:
            print(f"\nTesting with {data_name} data ({data_size} bytes):")
            test_data = secrets.token_bytes(data_size)
            
            for algorithm in signature_algorithms:
                print(f"  {algorithm.value}...", end=" ")
                
                try:
                    # Generate keypair once
                    keypair = self.signature_system.create_keypair(algorithm)
                    
                    # Benchmark signing
                    def sign_operation():
                        return self.signature_system.sign_message(
                            test_data, keypair.private_key, algorithm
                        )
                    
                    sign_measurements = self._measure_operation(sign_operation, MetricType.TIME)
                    
                    # Get sample signature for verification
                    sample_signature = sign_operation()
                    
                    # Benchmark verification
                    def verify_operation():
                        return self.signature_system.verify_signature(
                            test_data, sample_signature.signature, 
                            keypair.public_key, algorithm
                        )
                    
                    verify_measurements = self._measure_operation(verify_operation, MetricType.TIME)
                    
                    # Metadata
                    metadata = {
                        "data_size": data_size,
                        "signature_size": sample_signature.signature_size,
                        "public_key_size": keypair.key_size_public,
                        "private_key_size": keypair.key_size_private
                    }
                    
                    # Create results
                    sign_result = self._create_benchmark_result(
                        f"{algorithm.value}_{data_name}", BenchmarkType.SIGNING,
                        sign_measurements, MetricType.TIME, metadata
                    )
                    verify_result = self._create_benchmark_result(
                        f"{algorithm.value}_{data_name}", BenchmarkType.VERIFICATION,
                        verify_measurements, MetricType.TIME, metadata
                    )
                    
                    results.extend([sign_result, verify_result])
                    
                    print(f"✓ Sign: {sign_result.mean:.2f}ms, Verify: {verify_result.mean:.2f}ms")
                
                except Exception as e:
                    print(f"✗ Error: {e}")
        
        return results
    
    def benchmark_tls_handshakes(self) -> List[BenchmarkResult]:
        """Benchmark TLS handshake performance"""
        print("\n--- Benchmarking TLS Handshakes ---")
        results = []
        
        handshake_configs = [
            ("Classical_X25519", KeyExchangeType.CLASSICAL, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER768, None),
            ("Classical_ECDH_P256", KeyExchangeType.CLASSICAL, CryptoAlgorithm.ECDH_P256, CryptoAlgorithm.KYBER768, None),
            ("Hybrid_X25519_Kyber768", KeyExchangeType.DUAL_HYBRID, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER768, None),
            ("Hybrid_ECDH_P256_Kyber768", KeyExchangeType.DUAL_HYBRID, CryptoAlgorithm.ECDH_P256, CryptoAlgorithm.KYBER768, None),
            ("Triple_X25519_Kyber768_NTRU", KeyExchangeType.TRIPLE_HYBRID, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER768, CryptoAlgorithm.NTRU_HPS2048509),
            ("PQ_Only_Kyber768", KeyExchangeType.PQ_ONLY, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER768, None),
            ("PQ_Only_Kyber1024", KeyExchangeType.PQ_ONLY, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER1024, None)
        ]
        
        for config_name, exchange_type, classical_alg, pq_alg1, pq_alg2 in handshake_configs:
            print(f"  {config_name}...", end=" ")
            
            try:
                def handshake_operation():
                    handshake = HybridTLSHandshake(
                        exchange_type=exchange_type,
                        classical_alg=classical_alg,
                        pq_alg1=pq_alg1,
                        pq_alg2=pq_alg2
                    )
                    result = handshake.perform_handshake()
                    return result
                
                # Reduce iterations for handshakes (they're expensive)
                original_iterations = self.iterations
                self.iterations = min(100, self.iterations)
                
                measurements = self._measure_operation(handshake_operation, MetricType.TIME)
                
                # Restore iterations
                self.iterations = original_iterations
                
                # Get sample handshake for metadata
                sample_result = handshake_operation()
                
                metadata = {
                    "exchange_type": exchange_type.value,
                    "algorithms": sample_result["algorithms"],
                    "key_sizes": sample_result["key_sizes"],
                    "shared_secret_size": sample_result["shared_secret_size"]
                }
                
                result = self._create_benchmark_result(
                    config_name, BenchmarkType.HANDSHAKE,
                    measurements, MetricType.TIME, metadata
                )
                results.append(result)
                
                print(f"✓ {result.mean:.2f}ms avg")
            
            except Exception as e:
                print(f"✗ Error: {e}")
        
        return results
    
    def benchmark_client_server_performance(self) -> List[BenchmarkResult]:
        """Benchmark end-to-end client-server performance"""
        print("\n--- Benchmarking Client-Server Performance ---")
        results = []
        
        test_configs = [
            ("Classical_RSA", ConnectionMode.CLASSICAL, CryptoAlgorithm.X25519, 
             CryptoAlgorithm.KYBER768, SignatureAlgorithm.RSA_PSS_2048),
            ("Hybrid_Dilithium", ConnectionMode.HYBRID, CryptoAlgorithm.X25519, 
             CryptoAlgorithm.KYBER768, SignatureAlgorithm.DILITHIUM3),
            ("PQ_Only_Falcon", ConnectionMode.PQ_ONLY, CryptoAlgorithm.X25519, 
             CryptoAlgorithm.KYBER768, SignatureAlgorithm.FALCON512)
        ]
        
        base_port = 19000
        
        for i, (config_name, mode, classical_alg, pq_alg, sig_alg) in enumerate(test_configs):
            print(f"  {config_name}...", end=" ")
            port = base_port + i
            
            try:
                # Create configurations
                server_config = ServerConfig(
                    port=port, mode=mode, classical_alg=classical_alg,
                    pq_alg1=pq_alg, signature_alg=sig_alg, timeout=5.0
                )
                client_config = ClientConfig(
                    server_port=port, mode=mode, preferred_classical=classical_alg,
                    preferred_pq1=pq_alg, signature_alg=sig_alg, timeout=5.0
                )
                
                def full_protocol_test():
                    # Start server
                    server = QuantumSafeServer(server_config)
                    server_thread = threading.Thread(target=server.start, daemon=True)
                    server_thread.start()
                    time.sleep(0.1)  # Brief startup time
                    
                    try:
                        # Connect client and perform operations
                        client = QuantumSafeClient(client_config)
                        
                        start_time = time.perf_counter()
                        
                        if client.connect():
                            client.ping()
                            client.echo("test")
                            client.disconnect()
                            
                        end_time = time.perf_counter()
                        server.stop()
                        
                        return end_time - start_time
                    except:
                        server.stop()
                        raise
                
                # Reduce iterations for full protocol tests
                original_iterations = self.iterations
                self.iterations = min(50, self.iterations)
                
                measurements = []
                for _ in range(self.iterations):
                    try:
                        duration = full_protocol_test()
                        measurements.append(duration * 1000)  # Convert to ms
                        time.sleep(0.1)  # Brief pause between tests
                    except:
                        pass
                
                # Restore iterations
                self.iterations = original_iterations
                
                if measurements:
                    metadata = {
                        "mode": mode.value,
                        "classical_alg": classical_alg.value,
                        "pq_alg": pq_alg.value,
                        "signature_alg": sig_alg.value
                    }
                    
                    result = self._create_benchmark_result(
                        config_name, BenchmarkType.FULL_PROTOCOL,
                        measurements, MetricType.TIME, metadata
                    )
                    results.append(result)
                    
                    print(f"✓ {result.mean:.2f}ms avg")
                else:
                    print("✗ No successful measurements")
            
            except Exception as e:
                print(f"✗ Error: {e}")
        
        return results
    
    def run_comprehensive_benchmark(self) -> Dict[str, List[BenchmarkResult]]:
        """Run all benchmarks"""
        print("=== Comprehensive Cryptographic Performance Benchmark ===")
        print(f"System: {self.system_info.platform} - {self.system_info.cpu_count} CPUs")
        print(f"Iterations per test: {self.iterations}")
        
        all_results = {}
        
        # Key Generation
        all_results["key_generation"] = self.benchmark_key_generation()
        
        # Signing and Verification
        all_results["signing_verification"] = self.benchmark_signing_verification()
        
        # TLS Handshakes
        all_results["tls_handshakes"] = self.benchmark_tls_handshakes()
        
        # Client-Server Performance
        all_results["client_server"] = self.benchmark_client_server_performance()
        
        # Store all results
        self.results = []
        for category_results in all_results.values():
            self.results.extend(category_results)
        
        return all_results
    
    def generate_performance_report(self, output_dir: str = "benchmark_results"):
        """Generate comprehensive performance report"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n--- Generating Performance Report ---")
        
        # Create summary data
        summary_data = []
        for result in self.results:
            summary_data.append({
                "Algorithm": result.algorithm,
                "Benchmark": result.benchmark_type.value,
                "Metric": result.metric_type.value,
                "Mean": result.mean,
                "Median": result.median,
                "StdDev": result.std_dev,
                "Min": result.min_value,
                "Max": result.max_value,
                "P95": result.percentile_95,
                "P99": result.percentile_99,
                "Iterations": result.iterations
            })
        
        # Save CSV report
        csv_file = os.path.join(output_dir, "benchmark_results.csv")
        df = pd.DataFrame(summary_data)
        df.to_csv(csv_file, index=False)
        print(f"✓ CSV report saved: {csv_file}")
        
        # Save JSON report with full data
        json_file = os.path.join(output_dir, "benchmark_results.json")
        json_data = {
            "system_info": {
                "cpu_count": self.system_info.cpu_count,
                "cpu_freq": self.system_info.cpu_freq,
                "memory_total": self.system_info.memory_total,
                "python_version": self.system_info.python_version,
                "platform": self.system_info.platform,
                "timestamp": self.system_info.timestamp.isoformat()
            },
            "benchmark_config": {
                "iterations": self.iterations,
                "test_data_sizes": self.test_data_sizes
            },
            "results": summary_data
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"✓ JSON report saved: {json_file}")
        
        # Generate visualizations
        try:
            self._generate_visualizations(df, output_dir)
            print(f"✓ Visualizations saved to: {output_dir}")
        except Exception as e:
            print(f"⚠ Failed to generate visualizations: {e}")
        
        return output_dir
    
    def _generate_visualizations(self, df: pd.DataFrame, output_dir: str):
        """Generate performance visualization charts"""
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        # 1. Key Generation Performance Comparison
        keygen_data = df[df['Benchmark'] == 'key_generation'][df['Metric'] == 'time_ms']
        if not keygen_data.empty:
            plt.figure(figsize=(12, 8))
            
            # Separate classical and PQ algorithms
            classical_algs = keygen_data[keygen_data['Algorithm'].str.contains('RSA|ECDSA|Ed25519|X25519|X448|ECDH')]
            pq_algs = keygen_data[keygen_data['Algorithm'].str.contains('Dilithium|Falcon|Kyber|NTRU')]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            if not classical_algs.empty:
                ax1.bar(classical_algs['Algorithm'], classical_algs['Mean'])
                ax1.set_title('Classical Key Generation Performance')
                ax1.set_ylabel('Time (ms)')
                ax1.tick_params(axis='x', rotation=45)
            
            if not pq_algs.empty:
                ax2.bar(pq_algs['Algorithm'], pq_algs['Mean'])
                ax2.set_title('Post-Quantum Key Generation Performance')
                ax2.set_ylabel('Time (ms)')
                ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'key_generation_performance.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Signature Performance Comparison
        sign_data = df[df['Benchmark'] == 'signing'][df['Metric'] == 'time_ms']
        verify_data = df[df['Benchmark'] == 'verification'][df['Metric'] == 'time_ms']
        
        if not sign_data.empty and not verify_data.empty:
            plt.figure(figsize=(14, 8))
            
            # Extract algorithm names (remove data size suffix)
            sign_data_clean = sign_data.copy()
            sign_data_clean['Algorithm_Clean'] = sign_data_clean['Algorithm'].str.replace('_small|_medium|_large|_xlarge', '', regex=True)
            
            verify_data_clean = verify_data.copy()
            verify_data_clean['Algorithm_Clean'] = verify_data_clean['Algorithm'].str.replace('_small|_medium|_large|_xlarge', '', regex=True)
            
            # Group by algorithm and take mean
            sign_grouped = sign_data_clean.groupby('Algorithm_Clean')['Mean'].mean()
            verify_grouped = verify_data_clean.groupby('Algorithm_Clean')['Mean'].mean()
            
            x = np.arange(len(sign_grouped))
            width = 0.35
            
            plt.bar(x - width/2, sign_grouped.values, width, label='Signing', alpha=0.8)
            plt.bar(x + width/2, verify_grouped.values, width, label='Verification', alpha=0.8)
            
            plt.xlabel('Algorithm')
            plt.ylabel('Time (ms)')
            plt.title('Signing vs Verification Performance')
            plt.xticks(x, sign_grouped.index, rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'signature_performance.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. TLS Handshake Performance
        handshake_data = df[df['Benchmark'] == 'handshake'][df['Metric'] == 'time_ms']
        if not handshake_data.empty:
            plt.figure(figsize=(12, 6))
            
            plt.bar(handshake_data['Algorithm'], handshake_data['Mean'])
            plt.xlabel('Handshake Configuration')
            plt.ylabel('Time (ms)')
            plt.title('TLS Handshake Performance Comparison')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'handshake_performance.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Performance vs Security Trade-off
        plt.figure(figsize=(12, 8))
        
        # Create a scatter plot of performance vs key/signature sizes
        for result in self.results:
            if result.benchmark_type == BenchmarkType.SIGNING and result.metric_type == MetricType.TIME:
                signature_size = result.metadata.get('signature_size', 0)
                if signature_size > 0:
                    color = 'red' if any(pq in result.algorithm for pq in ['Dilithium', 'Falcon']) else 'blue'
                    plt.scatter(signature_size, result.mean, c=color, alpha=0.7, s=50)
                    plt.annotate(result.algorithm.split('_')[0], (signature_size, result.mean), 
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.xlabel('Signature Size (bytes)')
        plt.ylabel('Signing Time (ms)')
        plt.title('Performance vs Security Trade-off')
        plt.legend(['Post-Quantum', 'Classical'])
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_vs_security.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def print_summary(self):
        """Print benchmark summary to console"""
        if not self.results:
            print("No benchmark results to display")
            return
        
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        # Group results by benchmark type
        by_benchmark = {}
        for result in self.results:
            if result.benchmark_type not in by_benchmark:
                by_benchmark[result.benchmark_type] = []
            by_benchmark[result.benchmark_type].append(result)
        
        for benchmark_type, results in by_benchmark.items():
            print(f"\n{benchmark_type.value.upper()}:")
            print("-" * 50)
            
            # Group by metric type
            by_metric = {}
            for result in results:
                if result.metric_type not in by_metric:
                    by_metric[result.metric_type] = []
                by_metric[result.metric_type].append(result)
            
            for metric_type, metric_results in by_metric.items():
                print(f"\n{metric_type.value}:")
                
                # Sort by mean performance
                metric_results.sort(key=lambda x: x.mean)
                
                # Print top performers
                for i, result in enumerate(metric_results[:10]):  # Top 10
                    unit = "ms" if metric_type == MetricType.TIME else ("MB" if metric_type == MetricType.MEMORY else "")
                    print(f"  {i+1:2d}. {result.algorithm:<25} "
                          f"{result.mean:8.2f}{unit} (±{result.std_dev:.2f})")

# Example usage and testing
if __name__ == "__main__":
    print("=== Quantum-Safe Cryptography Performance Benchmark ===\n")
    
    # Create benchmark suite with reduced iterations for demo
    benchmark = CryptographicBenchmark(iterations=50)  # Reduced for demo
    
    try:
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark()
        
        # Print summary
        benchmark.print_summary()
        
        # Generate detailed report
        output_dir = benchmark.generate_performance_report()
        
        print(f"\n=== Benchmark Complete ===")
        print(f"Total tests run: {len(benchmark.results)}")
        print(f"Results saved to: {output_dir}")
        
        # Quick performance insights
        print("\n=== Key Performance Insights ===")
        
        # Fastest key generation
        keygen_results = [r for r in benchmark.results 
                         if r.benchmark_type == BenchmarkType.KEY_GENERATION and r.metric_type == MetricType.TIME]
        if keygen_results:
            fastest_keygen = min(keygen_results, key=lambda x: x.mean)
            print(f"Fastest Key Generation: {fastest_keygen.algorithm} ({fastest_keygen.mean:.2f}ms)")
        
        # Fastest signing
        sign_results = [r for r in benchmark.results 
                       if r.benchmark_type == BenchmarkType.SIGNING and r.metric_type == MetricType.TIME]
        if sign_results:
            fastest_sign = min(sign_results, key=lambda x: x.mean)
            print(f"Fastest Signing: {fastest_sign.algorithm} ({fastest_sign.mean:.2f}ms)")
        
        # Fastest handshake
        handshake_results = [r for r in benchmark.results 
                           if r.benchmark_type == BenchmarkType.HANDSHAKE and r.metric_type == MetricType.TIME]
        if handshake_results:
            fastest_handshake = min(handshake_results, key=lambda x: x.mean)
            print(f"Fastest Handshake: {fastest_handshake.algorithm} ({fastest_handshake.mean:.2f}ms)")
        
        print(f"\nFor detailed analysis, see the generated reports in: {output_dir}")
    
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
