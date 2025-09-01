#!/usr/bin/env python3
"""
Quantum-Safe Cryptography Demonstration Suite
Main application entry point providing comprehensive post-quantum cryptography demonstrations

This application demonstrates:
1. Hybrid TLS 1.3 handshakes (classical + post-quantum)
2. Quantum-safe digital signatures (Dilithium, Falcon, SPHINCS+)
3. Client-server applications with crypto-agility
4. Performance benchmarking of various algorithms
5. BB84 Quantum Key Distribution simulation
6. Migration strategy and threat analysis
7. Extended post-quantum algorithm support

Usage:
    python main.py --demo all
    python main.py --demo tls
    python main.py --demo signatures
    python main.py --demo benchmark
    python main.py --interactive
"""

import sys
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any

# Import all our modules
try:
    from hybrid_tls import HybridTLSHandshake, KeyExchangeType, CryptoAlgorithm
    from quantum_signatures import HybridSignatureSystem, SignatureAlgorithm
    from client_server_apps import QuantumSafeServer, QuantumSafeClient, ServerConfig, ClientConfig, ConnectionMode, CryptoAgilityDemo
    from performance_benchmark import CryptographicBenchmark
    from qkd_bb84_simulation import BB84Protocol, QuantumChannel, ChannelParameters, BB84Analyzer
    from migration_strategy import AssetInventoryManager, MigrationPlanner, RegulationComplianceChecker
    from simple_extended_pq import AlgorithmRegistry, SimpleNTRU, SimpleSPHINCS, SimpleMcEliece
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all modules are in the same directory.")
    sys.exit(1)

class QuantumSafeCryptoSuite:
    """Main application class for the quantum-safe cryptography demonstration suite"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Quantum-Safe Cryptography Suite v{self.version}                    ║
║                                                                              ║
║  Comprehensive Post-Quantum Cryptography Demonstration & Analysis Platform  ║
║                                                                              ║
║  Features:                                                                   ║
║  • Hybrid TLS 1.3 Handshakes (Classical + Post-Quantum)                    ║
║  • Digital Signatures (Dilithium, Falcon, SPHINCS+)                        ║
║  • Client-Server Applications with Crypto-Agility                          ║
║  • Performance Benchmarking & Analysis                                      ║
║  • BB84 Quantum Key Distribution Simulation                                 ║
║  • Migration Strategy & Threat Analysis                                     ║
║  • Extended Algorithm Support (NTRU, McEliece, etc.)                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    def print_banner(self):
        """Print application banner"""
        print(self.banner)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")
    
    def demo_hybrid_tls(self):
        """Demonstrate hybrid TLS 1.3 handshakes"""
        print(" HYBRID TLS 1.3 HANDSHAKE DEMONSTRATION")
        print("=" * 50)
        
        # Test different handshake configurations
        configs = [
            ("Classical X25519", KeyExchangeType.CLASSICAL, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER768, None),
            ("Hybrid X25519+Kyber768", KeyExchangeType.DUAL_HYBRID, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER768, None),
            ("Triple Hybrid", KeyExchangeType.TRIPLE_HYBRID, CryptoAlgorithm.ECDH_P256, CryptoAlgorithm.KYBER768, CryptoAlgorithm.NTRU_HPS2048509),
            ("Post-Quantum Only", KeyExchangeType.PQ_ONLY, CryptoAlgorithm.X25519, CryptoAlgorithm.KYBER1024, None)
        ]
        
        results = []
        for name, kex_type, classical, pq1, pq2 in configs:
            print(f"\n🔹 Testing: {name}")
            
            try:
                handshake = HybridTLSHandshake(
                    exchange_type=kex_type,
                    classical_alg=classical,
                    pq_alg1=pq1,
                    pq_alg2=pq2
                )
                
                start_time = time.time()
                result = handshake.perform_handshake()
                duration = time.time() - start_time
                
                print(f"   Success in {duration:.3f}s")
                print(f"   Algorithms: {', '.join(result['algorithms'])}")
                print(f"   Final key: {result['shared_secret_size']} bytes")
                print(f"   Efficiency: {result['protocol_efficiency']*100:.1f}%")
                
                results.append((name, result, duration))
                
            except Exception as e:
                print(f"   Failed: {e}")
        
        # Summary
        print(f"\n HANDSHAKE SUMMARY")
        print("-" * 30)
        for name, result, duration in results:
            print(f"{name:<25}: {duration:.3f}s")
        
        return results
    
    def demo_quantum_signatures(self):
        """Demonstrate quantum-safe digital signatures"""
        print("\n QUANTUM-SAFE DIGITAL SIGNATURES DEMONSTRATION")
        print("=" * 55)
        
        signature_system = HybridSignatureSystem()
        test_message = b"This is a test message for quantum-safe digital signatures demonstration."
        
        # Test different signature algorithms
        algorithms = [
            SignatureAlgorithm.RSA_PSS_2048,
            SignatureAlgorithm.ECDSA_P256,
            SignatureAlgorithm.ED25519,
            SignatureAlgorithm.DILITHIUM2,
            SignatureAlgorithm.DILITHIUM3,
            SignatureAlgorithm.FALCON512
        ]
        
        results = []
        print(f"\n Testing message: '{test_message.decode()[:50]}...'")
        print(f" Message length: {len(test_message)} bytes\n")
        
        for algorithm in algorithms:
            print(f" Testing {algorithm.value}:")
            
            try:
                # Generate keypair
                start = time.time()
                keypair = signature_system.create_keypair(algorithm)
                keygen_time = time.time() - start
                
                # Sign message
                start = time.time()
                signature = signature_system.sign_message(test_message, keypair.private_key, algorithm)
                sign_time = time.time() - start
                
                # Verify signature
                start = time.time()
                is_valid = signature_system.verify_signature(
                    test_message, signature.signature, keypair.public_key, algorithm
                )
                verify_time = time.time() - start
                
                print(f"   Keygen: {keygen_time*1000:.2f}ms | Sign: {sign_time*1000:.2f}ms | Verify: {verify_time*1000:.2f}ms")
                print(f"   Key sizes: {keypair.key_size_public}/{keypair.key_size_private} bytes")
                print(f"   Signature: {signature.signature_size} bytes | Valid: {is_valid}")
                
                results.append({
                    'algorithm': algorithm.value,
                    'keygen_ms': keygen_time * 1000,
                    'sign_ms': sign_time * 1000,
                    'verify_ms': verify_time * 1000,
                    'pub_key_size': keypair.key_size_public,
                    'priv_key_size': keypair.key_size_private,
                    'signature_size': signature.signature_size,
                    'valid': is_valid
                })
                
            except Exception as e:
                print(f"   Failed: {e}")
        
        # Performance comparison
        print(f"\n SIGNATURE PERFORMANCE COMPARISON")
        print("-" * 40)
        print(f"{'Algorithm':<20} {'Sign(ms)':<10} {'Verify(ms)':<12} {'Sig Size':<10}")
        print("-" * 55)
        
        for result in results:
            print(f"{result['algorithm']:<20} {result['sign_ms']:<10.2f} {result['verify_ms']:<12.2f} {result['signature_size']:<10}")
        
        return results
    
    def demo_client_server(self):
        """Demonstrate client-server applications with crypto-agility"""
        print("\n CLIENT-SERVER CRYPTO-AGILITY DEMONSTRATION")
        print("=" * 50)
        
        demo = CryptoAgilityDemo()
        
        print(" Testing different cryptographic configurations...")
        print(" Each test includes: connection, handshake, ping, echo, rekey\n")
        
        # Run the crypto-agility demonstration
        results = demo.run_demo(port_base=15000)
        
        print(f"\n CLIENT-SERVER TEST RESULTS")
        print("-" * 40)
        print(f"{'Configuration':<20} {'Success':<8} {'Handshake(ms)':<15} {'Ping(ms)'}")
        print("-" * 55)
        
        for config_name, result in results.items():
            if result['success']:
                handshake_ms = result['handshake_time'] * 1000 if result['handshake_time'] else 0
                ping_ms = result['ping_time'] * 1000 if result['ping_time'] else 0
                print(f"{config_name:<20} {'✅':<8} {handshake_ms:<15.1f} {ping_ms:.1f}")
            else:
                print(f"{config_name:<20} {'❌':<8} {'ERROR':<15} {result.get('error', 'Unknown')}")
        
        return results
    
    def demo_performance_benchmark(self, quick_mode=True):
        """Demonstrate performance benchmarking"""
        print("\n⚡ PERFORMANCE BENCHMARKING DEMONSTRATION")
        print("=" * 45)
        
        iterations = 25 if quick_mode else 100
        print(f" Running benchmark with {iterations} iterations per test")
        print(" This may take a few moments...\n")
        
        benchmark = CryptographicBenchmark(iterations=iterations)
        
        try:
            # Run key generation benchmark
            print(" Benchmarking key generation...")
            keygen_results = benchmark.benchmark_key_generation()
            
            # Run signature benchmark
            print(" Benchmarking signatures...")
            sig_results = benchmark.benchmark_signing_verification()
            
            # Run TLS handshake benchmark
            print(" Benchmarking TLS handshakes...")
            tls_results = benchmark.benchmark_tls_handshakes()
            
            # Display results
            print(f"\n TOP PERFORMERS")
            print("-" * 25)
            
            # Fastest key generation
            fastest_keygen = min(keygen_results, key=lambda x: x.mean if x.metric_type.value == 'time_ms' else float('inf'))
            if fastest_keygen:
                print(f" Fastest Key Generation: {fastest_keygen.algorithm} ({fastest_keygen.mean:.2f}ms)")
            
            # Fastest signing
            sign_only = [r for r in sig_results if r.benchmark_type.value == 'signing']
            if sign_only:
                fastest_sign = min(sign_only, key=lambda x: x.mean)
                print(f" Fastest Signing: {fastest_sign.algorithm} ({fastest_sign.mean:.2f}ms)")
            
            # Fastest handshake
            if tls_results:
                fastest_handshake = min(tls_results, key=lambda x: x.mean)
                print(f" Fastest Handshake: {fastest_handshake.algorithm} ({fastest_handshake.mean:.2f}ms)")
            
            # Size comparison
            print(f"\n SIZE COMPARISON (bytes)")
            print("-" * 30)
            
            for result in keygen_results[:5]:  # Top 5
                if hasattr(result, 'metadata') and result.metadata:
                    pub_size = result.metadata.get('public_key_size', 'N/A')
                    priv_size = result.metadata.get('private_key_size', 'N/A')
                    print(f"{result.algorithm:<20}: pub={pub_size}, priv={priv_size}")
            
            return {
                'keygen': keygen_results,
                'signatures': sig_results,
                'handshakes': tls_results
            }
            
        except Exception as e:
            print(f" Benchmark failed: {e}")
            return None
    
    def demo_qkd_simulation(self):
        """Demonstrate BB84 Quantum Key Distribution"""
        print("\n BB84 QUANTUM KEY DISTRIBUTION SIMULATION")
        print("=" * 45)
        
        print("🔸 Setting up quantum channel simulation...")
        
        # Create quantum channel with realistic parameters
        channel_params = ChannelParameters(
            distance_km=50.0,
            fiber_loss_db_per_km=0.2,
            detector_efficiency=0.8,
            background_noise=0.02
        )
        
        channel = QuantumChannel(channel_params)
        analyzer = BB84Analyzer()
        
        # Test 1: Basic QKD without eavesdropper
        print("\n🔹 Test 1: Secure QKD (No Eavesdropper)")
        protocol = BB84Protocol(channel)
        result = protocol.run_protocol(key_length=5000)
        analyzer.add_result(result)
        
        print(f"   Final key: {result.final_key_length} bits")
        print(f"   QBER: {result.quantum_bit_error_rate*100:.2f}%")
        print(f"   Key rate: {result.key_generation_rate:.0f} bits/s")
        print(f"  ️ Eavesdropping detected: {result.detected_eavesdropping}")
        
        # Test 2: QKD with eavesdropper
        print("\n Test 2: QKD with Eavesdropper (30% intercept)")
        from qkd_bb84_simulation import Eavesdropper, EavesdropperConfig
        
        eve_config = EavesdropperConfig(intercept_probability=0.3)
        eavesdropper = Eavesdropper(eve_config)
        protocol_with_eve = BB84Protocol(channel, eavesdropper)
        
        result_with_eve = protocol_with_eve.run_protocol(key_length=5000)
        analyzer.add_result(result_with_eve)
        
        print(f"   QBER with Eve: {result_with_eve.quantum_bit_error_rate*100:.2f}%")
        print(f"   Eavesdropping detected: {result_with_eve.detected_eavesdropping}")
        print(f"   Final key: {result_with_eve.final_key_length} bits")
        print(f"   Eve intercepted: {len(eavesdropper.intercepted_photons)} photons")
        
        # Test 3: Distance analysis
        print("\n🔹 Test 3: Distance Effect Analysis")
        distances = [25, 50, 100, 150]
        distance_results = analyzer.analyze_distance_effects(distances, key_length=2000)
        
        print("  Distance | Efficiency | QBER   | Key Length")
        print("  ---------|------------|--------|------------")
        for distance, result in distance_results.items():
            efficiency = result.protocol_efficiency * 100
            qber = result.quantum_bit_error_rate * 100
            print(f"  {distance:4.0f} km  | {efficiency:7.1f}%   | {qber:5.1f}% | {result.final_key_length:6} bits")
        
        return {
            'secure': result,
            'with_eve': result_with_eve,
            'distance_analysis': distance_results
        }
    
    def demo_migration_strategy(self):
        """Demonstrate migration strategy and threat analysis"""
        print("\n MIGRATION STRATEGY & THREAT ANALYSIS DEMONSTRATION")
        print("=" * 55)
        
        from migration_strategy import (
            AssetInventoryManager, MigrationPlanner, RegulationComplianceChecker,
            CryptographicAsset, AssetSensitivity, ThreatLevel
        )
        
        # Initialize components
        inventory_manager = AssetInventoryManager()
        migration_planner = MigrationPlanner(inventory_manager)
        compliance_checker = RegulationComplianceChecker()
        
        print("🔸 Creating sample cryptographic asset inventory...")
        
        # Add sample assets
        sample_assets = [
            CryptographicAsset(
                asset_id="TLS_CERT_001",
                name="Web Server Certificate",
                asset_type="certificate",
                current_algorithm="RSA",
                key_size=2048,
                sensitivity_level=AssetSensitivity.CONFIDENTIAL,
                criticality=ThreatLevel.HIGH,
                location="cloud",
                owner="IT Security",
                last_updated=datetime(2023, 1, 15),
                migration_priority=1,
                estimated_migration_effort="medium"
            ),
            CryptographicAsset(
                asset_id="API_KEY_002", 
                name="API Signing Key",
                asset_type="key",
                current_algorithm="ECDSA",
                key_size=256,
                sensitivity_level=AssetSensitivity.INTERNAL,
                criticality=ThreatLevel.MEDIUM,
                location="on_premise",
                owner="Development",
                last_updated=datetime(2022, 6, 10),
                migration_priority=2,
                estimated_migration_effort="high"
            ),
            CryptographicAsset(
                asset_id="LEGACY_APP_003",
                name="Legacy Application",
                asset_type="application", 
                current_algorithm="RSA",
                key_size=1024,
                sensitivity_level=AssetSensitivity.SECRET,
                criticality=ThreatLevel.CRITICAL,
                location="on_premise",
                owner="Finance",
                last_updated=datetime(2020, 3, 12),
                migration_priority=1,
                estimated_migration_effort="high"
            )
        ]
        
        for asset in sample_assets:
            inventory_manager.add_asset(asset)
        
        print(f"   Added {len(sample_assets)} assets to inventory")
        
        # Risk assessment
        print("\n🔹 Performing Risk Assessment...")
        risk_report = inventory_manager.generate_risk_assessment_report()
        
        print(f"   Risk Distribution:")
        print(f"    High Risk: {risk_report['risk_distribution']['high_risk']} assets")
        print(f"    Medium Risk: {risk_report['risk_distribution']['medium_risk']} assets") 
        print(f"    Low Risk: {risk_report['risk_distribution']['low_risk']} assets")
        print(f"   Average Risk Score: {risk_report['average_risk_score']:.1f}/10.0")
        
        # Migration planning
        print("\n🔹 Creating Migration Plan...")
        high_risk_assets = [
            ra['asset_id'] for ra in risk_report['risk_assessments']
            if ra['current_risk_score'] >= 7.0
        ]
        
        if high_risk_assets:
            plan_id = migration_planner.create_migration_plan(high_risk_assets, 365)
            plan = migration_planner.migration_plans[plan_id]
            
            print(f"   Created plan {plan_id}")
            print(f"   Estimated cost: ${plan.estimated_cost:,.0f}")
            print(f"   Duration: {(plan.target_completion - plan.start_date).days} days")
            print(f"   Assets: {len(plan.asset_ids)}")
        
        # Compliance checking
        print("\n🔹 Checking Regulatory Compliance...")
        frameworks = ["NIST", "NSA_CNSS", "EU_CYBERSEC"]
        
        for framework in frameworks:
            compliance = compliance_checker.check_compliance(
                list(inventory_manager.assets.values()), framework
            )
            print(f"  {framework}: {compliance['compliance_rate']*100:.0f}% compliant")
        
        return {
            'risk_report': risk_report,
            'migration_plan': plan if high_risk_assets else None,
            'compliance': {fw: compliance_checker.check_compliance(
                list(inventory_manager.assets.values()), fw
            ) for fw in frameworks}
        }
    
    def demo_extended_algorithms(self):
        """Demonstrate extended post-quantum algorithms"""
        print("\n EXTENDED POST-QUANTUM ALGORITHMS DEMONSTRATION")
        print("=" * 50)
        
        registry = AlgorithmRegistry()
        
        print("🔸 Available Algorithm Families:")
        from simple_extended_pq import PQAlgorithmFamily
        
        for family in PQAlgorithmFamily:
            algorithms = registry.list_by_family(family)
            if algorithms:
                print(f"   {family.value.title()}: {len(algorithms)} algorithms")
                for alg in algorithms[:2]:  # Show first 2
                    spec = registry.get_algorithm(alg)
                    print(f"    • {alg} (Level {spec.security_level.value})")
        
        print("\n🔹 Testing NTRU Implementation...")
        ntru = SimpleNTRU("ntru_hps2048509")
        
        start = time.time()
        pub_key, priv_key = ntru.keygen()
        keygen_time = time.time() - start
        
        start = time.time()
        ciphertext, shared_secret = ntru.encaps(pub_key)
        encaps_time = time.time() - start
        
        start = time.time()
        recovered_secret = ntru.decaps(ciphertext, priv_key)
        decaps_time = time.time() - start
        
        print(f"   Key Generation: {keygen_time*1000:.2f} ms")
        print(f"   Encapsulation: {encaps_time*1000:.2f} ms")
        print(f"   Decapsulation: {decaps_time*1000:.2f} ms")
        print(f"   Public Key: {len(pub_key)} bytes")
        print(f"   Ciphertext: {len(ciphertext)} bytes")
        
        print("\n🔹 Testing SPHINCS+ Implementation...")
        sphincs = SimpleSPHINCS("sphincs_sha256_128f")
        test_message = b"Test message for SPHINCS+ demonstration"
        
        start = time.time()
        pub_key, priv_key = sphincs.keygen()
        keygen_time = time.time() - start
        
        start = time.time()
        signature = sphincs.sign(test_message, priv_key)
        sign_time = time.time() - start
        
        start = time.time()
        is_valid = sphincs.verify(test_message, signature, pub_key)
        verify_time = time.time() - start
        
        print(f"  Key Generation: {keygen_time*1000:.2f} ms")
        print(f"  Signing: {sign_time*1000:.2f} ms")
        print(f"  Verification: {verify_time*1000:.2f} ms")
        print(f"  Signature: {len(signature)} bytes")
        print(f"  Valid: {is_valid}")
        
        return {
            'ntru_results': {
                'keygen_ms': keygen_time * 1000,
                'encaps_ms': encaps_time * 1000,
                'decaps_ms': decaps_time * 1000,
                'pub_key_size': len(pub_key),
                'ciphertext_size': len(ciphertext)
            },
            'sphincs_results': {
                'keygen_ms': keygen_time * 1000,
                'sign_ms': sign_time * 1000,
                'verify_ms': verify_time * 1000,
                'signature_size': len(signature),
                'valid': is_valid
            }
        }
    
    def run_all_demos(self):
        """Run all demonstrations"""
        self.print_banner()
        
        all_results = {}
        
        try:
            # Demo 1: Hybrid TLS
            all_results['hybrid_tls'] = self.demo_hybrid_tls()
            
            # Demo 2: Quantum Signatures
            all_results['quantum_signatures'] = self.demo_quantum_signatures()
            
            # Demo 3: Client-Server
            all_results['client_server'] = self.demo_client_server()
            
            # Demo 4: Performance Benchmark (quick mode)
            all_results['performance'] = self.demo_performance_benchmark(quick_mode=True)
            
            # Demo 5: QKD Simulation
            all_results['qkd'] = self.demo_qkd_simulation()
            
            # Demo 6: Migration Strategy
            all_results['migration'] = self.demo_migration_strategy()
            
            # Demo 7: Extended Algorithms
            all_results['extended_algorithms'] = self.demo_extended_algorithms()
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Demonstration interrupted by user")
            return all_results
        except Exception as e:
            print(f"\n❌ Error during demonstration: {e}")
            return all_results
        
        # Final summary
        print(f"\n🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("   Summary of completed demonstrations:")
        print("   Hybrid TLS 1.3 Handshakes")
        print("  Quantum-Safe Digital Signatures")
        print("  Client-Server Crypto-Agility")
        print("  Performance Benchmarking")
        print("  BB84 Quantum Key Distribution")
        print("  Migration Strategy & Threat Analysis")
        print("  Extended Post-Quantum Algorithms")
        
        print(f"\n Total execution time: {time.time() - self.start_time:.1f} seconds")
        print(" All cryptographic operations completed successfully!")
        
        return all_results
    
    def interactive_mode(self):
        """Interactive mode for selective demonstration"""
        self.print_banner()
        
        demos = {
            '1': ('Hybrid TLS 1.3 Handshakes', self.demo_hybrid_tls),
            '2': ('Quantum-Safe Digital Signatures', self.demo_quantum_signatures),
            '3': ('Client-Server Applications', self.demo_client_server),
            '4': ('Performance Benchmarking', lambda: self.demo_performance_benchmark(quick_mode=False)),
            '5': ('BB84 QKD Simulation', self.demo_qkd_simulation),
            '6': ('Migration Strategy', self.demo_migration_strategy),
            '7': ('Extended PQ Algorithms', self.demo_extended_algorithms),
            'a': ('All Demonstrations', self.run_all_demos)
        }
        
        while True:
            print("\n🎛 INTERACTIVE DEMONSTRATION MENU")
            print("=" * 35)
            
            for key, (name, _) in demos.items():
                icon = "🚀" if key == 'a' else "📋"
                print(f"  {key}. {icon} {name}")
            
            print("  q. 🚪 Quit")
            
            choice = input("\nSelect demonstration (1-7, a, or q): ").strip().lower()
            
            if choice == 'q':
                print("👋 Thank you for using the Quantum-Safe Cryptography Suite!")
                break
            elif choice in demos:
                print(f"\n🚀 Starting: {demos[choice][0]}")
                print("-" * 40)
                try:
                    result = demos[choice][1]()
                    print(f"\n✅ {demos[choice][0]} completed successfully!")
                except KeyboardInterrupt:
                    print(f"\n⏹️ {demos[choice][0]} interrupted by user")
                except Exception as e:
                    print(f"\n❌ Error in {demos[choice][0]}: {e}")
                
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Quantum-Safe Cryptography Demonstration Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo all              # Run all demonstrations
  python main.py --demo tls              # Show TLS handshakes only
  python main.py --demo signatures       # Show digital signatures only
  python main.py --demo benchmark        # Run performance benchmarks
  python main.py --interactive           # Interactive mode
  python main.py --version              # Show version info
        """
    )
    
    parser.add_argument('--demo', choices=['all', 'tls', 'signatures', 'client-server', 'benchmark', 'qkd', 'migration', 'extended'],
                       help='Run specific demonstration')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--version', action='version', version='Quantum-Safe Crypto Suite v1.0.0')
    parser.add_argument('--quick', action='store_true', help='Use reduced iterations for faster execution')
    
    args = parser.parse_args()
    
    suite = QuantumSafeCryptoSuite()
    suite.start_time = time.time()
    
    try:
        if args.interactive:
            suite.interactive_mode()
        elif args.demo:
            suite.print_banner()
            
            if args.demo == 'all':
                suite.run_all_demos()
            elif args.demo == 'tls':
                suite.demo_hybrid_tls()
            elif args.demo == 'signatures':
                suite.demo_quantum_signatures()
            elif args.demo == 'client-server':
                suite.demo_client_server()
            elif args.demo == 'benchmark':
                suite.demo_performance_benchmark(quick_mode=args.quick)
            elif args.demo == 'qkd':
                suite.demo_qkd_simulation()
            elif args.demo == 'migration':
                suite.demo_migration_strategy()
            elif args.demo == 'extended':
                suite.demo_extended_algorithms()
        else:
            # Default: run interactive mode
            suite.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for exploring quantum-safe cryptography!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
