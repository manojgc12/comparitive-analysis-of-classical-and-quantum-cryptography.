# Quantum-Safe Cryptography Suite v1.0.0

A comprehensive Python-based demonstration and analysis platform for post-quantum cryptography, designed for research, education, and migration planning.

## 🔐 Overview

This suite provides hands-on experience with quantum-safe cryptographic algorithms and protocols, including:

- **Hybrid TLS 1.3 Handshakes** - Classical + post-quantum key exchange
- **Digital Signatures** - Dilithium, Falcon, SPHINCS+ implementations
- **Client-Server Applications** - Crypto-agile networking demonstrations
- **Performance Benchmarking** - Comprehensive algorithm comparison
- **BB84 QKD Simulation** - Quantum key distribution with eavesdropping analysis
- **Migration Strategy Tools** - Risk assessment and compliance checking
- **Extended Algorithm Support** - NTRU, McEliece, and more

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (tested on Windows, adaptable to Linux/macOS)
- PyCharm IDE (recommended) or any Python IDE
- 4GB RAM minimum, 8GB recommended

### Installation

1. **Clone or download** the project to your desired directory:
   ```
   quantum_safe_crypto/
   ```

2. **Install dependencies**:
   ```bash
   cd quantum_safe_crypto
   pip install -r requirements.txt
   ```

3. **Run the main application**:
   ```bash
   python main.py --interactive
   ```

### First Run

Start with the interactive mode to explore different demonstrations:

```bash
python main.py --interactive
```

This will present a menu allowing you to select specific demonstrations or run all tests.

## 📋 Usage Examples

### Command Line Options

```bash
# Run all demonstrations
python main.py --demo all

# Run specific demonstrations
python main.py --demo tls              # Hybrid TLS handshakes
python main.py --demo signatures       # Digital signatures
python main.py --demo benchmark        # Performance benchmarks
python main.py --demo qkd              # Quantum key distribution
python main.py --demo migration        # Migration planning
python main.py --demo extended         # Extended algorithms

# Interactive mode (recommended for first-time users)
python main.py --interactive

# Quick benchmarks (fewer iterations)
python main.py --demo benchmark --quick
```

### PyCharm Integration

1. **Open PyCharm** and create a new project
2. **Set the project directory** to `quantum_safe_crypto`
3. **Configure the Python interpreter** to use your environment with installed dependencies
4. **Run configurations**:
   - Main script: `main.py`
   - Working directory: `quantum_safe_crypto`
   - Parameters: `--interactive` (or any other options)

## 🏗️ Project Structure

```
quantum_safe_crypto/
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── README.md                   # This documentation
├── DEVELOPER_GUIDE.md          # Developer documentation
├── hybrid_tls.py               # Hybrid TLS 1.3 implementation
├── quantum_signatures.py       # Digital signature systems
├── client_server_apps.py       # Networking applications
├── performance_benchmark.py    # Benchmarking framework
├── qkd_bb84_simulation.py      # Quantum key distribution
├── migration_strategy.py       # Migration planning tools
└── simple_extended_pq.py       # Extended algorithm support
```

## 🔧 Core Components

### 1. Hybrid TLS 1.3 Handshakes (`hybrid_tls.py`)

Demonstrates secure key exchange using combinations of classical and post-quantum algorithms:

- **Classical**: X25519, ECDH P-256/P-384
- **Post-Quantum**: Kyber (512/768/1024), NTRU, Saber
- **Modes**: Classical-only, Hybrid (classical+PQ), Triple-hybrid, PQ-only

**Example Usage**:
```python
from hybrid_tls import HybridTLSHandshake, KeyExchangeType, CryptoAlgorithm

# Create hybrid handshake
handshake = HybridTLSHandshake(
    exchange_type=KeyExchangeType.DUAL_HYBRID,
    classical_alg=CryptoAlgorithm.X25519,
    pq_alg1=CryptoAlgorithm.KYBER768
)

# Perform handshake
result = handshake.perform_handshake()
print(f"Shared secret: {result['shared_secret_size']} bytes")
```

### 2. Quantum-Safe Digital Signatures (`quantum_signatures.py`)

Implements multiple signature algorithms with crypto-agility support:

- **Classical**: RSA-PSS, ECDSA, Ed25519
- **Post-Quantum**: Dilithium (2/3/5), Falcon (512/1024), SPHINCS+
- **Features**: Certificate authority, hybrid signatures, benchmarking

**Example Usage**:
```python
from quantum_signatures import HybridSignatureSystem, SignatureAlgorithm

system = HybridSignatureSystem()

# Generate keypair
keypair = system.create_keypair(SignatureAlgorithm.DILITHIUM3)

# Sign and verify
signature = system.sign_message(b"test message", keypair.private_key, SignatureAlgorithm.DILITHIUM3)
is_valid = system.verify_signature(b"test message", signature.signature, keypair.public_key, SignatureAlgorithm.DILITHIUM3)
```

### 3. Client-Server Applications (`client_server_apps.py`)

Demonstrates practical quantum-safe networking:

- **Multi-threaded server** with session management
- **Crypto-agile client** supporting algorithm switching
- **Protocol operations**: handshake, ping, echo, rekey
- **Configuration management** for different security levels

### 4. Performance Benchmarking (`performance_benchmark.py`)

Comprehensive performance analysis framework:

- **Metrics**: Key generation, signing, verification, handshake times
- **Memory usage** tracking and analysis
- **Statistical analysis** with confidence intervals
- **Export formats**: CSV, JSON, graphical reports

### 5. BB84 Quantum Key Distribution (`qkd_bb84_simulation.py`)

Realistic QKD protocol simulation:

- **Quantum channel** modeling with noise and loss
- **Eavesdropping detection** with multiple attack strategies
- **Distance analysis** and key rate calculations
- **Error correction** and privacy amplification

### 6. Migration Strategy Tools (`migration_strategy.py`)

Enterprise-grade migration planning:

- **Asset inventory** management with risk scoring
- **Threat analysis** against quantum attacks
- **Migration planning** with cost estimation
- **Regulatory compliance** checking (NIST, NSA, EU frameworks)

### 7. Extended Algorithm Support (`simple_extended_pq.py`)

Additional post-quantum implementations:

- **NTRU** key encapsulation mechanism
- **SPHINCS+** hash-based signatures  
- **Classic McEliece** code-based cryptography
- **Algorithm registry** for extensibility

## 📊 Demonstration Scenarios

### Scenario 1: TLS Security Assessment

Compare different handshake configurations:
```bash
python main.py --demo tls
```

**Output**: Performance comparison of classical vs. hybrid vs. post-quantum-only handshakes.

### Scenario 2: Signature Algorithm Migration

Evaluate signature performance for migration planning:
```bash
python main.py --demo signatures
```

**Output**: Detailed comparison of classical and post-quantum signature sizes and speeds.

### Scenario 3: Network Application Testing

Test crypto-agility in client-server applications:
```bash
python main.py --demo client-server
```

**Output**: Success rates and performance metrics for different cryptographic configurations.

### Scenario 4: Quantum Attack Simulation

Simulate eavesdropping on quantum key distribution:
```bash
python main.py --demo qkd
```

**Output**: QBER analysis, eavesdropping detection, and secure key rates.

## 🔬 Research Applications

### Academic Research

- **Algorithm comparison** across multiple metrics
- **Performance analysis** on different hardware
- **Security parameter** optimization studies
- **Protocol efficiency** measurements

### Industry Applications

- **Migration risk assessment** for existing systems
- **Compliance verification** against regulatory standards
- **Performance benchmarking** for specific use cases
- **Proof-of-concept** development for hybrid systems

## 🛠️ Configuration

### Algorithm Selection

Most modules support algorithm selection through enumerations:

```python
# TLS key exchange algorithms
CryptoAlgorithm.X25519          # Classical ECDH
CryptoAlgorithm.KYBER768        # Post-quantum KEM
CryptoAlgorithm.NTRU_HPS2048509 # Alternative PQ

# Signature algorithms
SignatureAlgorithm.DILITHIUM3   # Lattice-based
SignatureAlgorithm.FALCON512    # NTRU-based  
SignatureAlgorithm.RSA_PSS_2048 # Classical
```

### Performance Tuning

Adjust benchmark parameters for your environment:

```python
# Quick testing (25 iterations)
python main.py --demo benchmark --quick

# Thorough analysis (100+ iterations)
python main.py --demo benchmark
```

### Security Levels

Configure security levels to match requirements:

```python
# Conservative (high security, slower)
SecurityLevel.LEVEL_5  # 256-bit equivalent

# Balanced (good security, practical speed)
SecurityLevel.LEVEL_3  # 192-bit equivalent

# Fast (baseline security, high speed)
SecurityLevel.LEVEL_1  # 128-bit equivalent
```

## 📈 Performance Expectations

### Typical Performance (on modern hardware)

| Operation | Classical | Post-Quantum | Hybrid |
|-----------|----------|--------------|--------|
| Key Generation | 1-5 ms | 5-50 ms | 10-60 ms |
| Signing | 0.1-2 ms | 10-100 ms | 15-110 ms |
| Verification | 0.1-5 ms | 1-20 ms | 5-25 ms |
| Handshake | 5-20 ms | 50-200 ms | 60-250 ms |

*Note: Performance varies significantly based on algorithm choice, security level, and hardware.*

### Memory Requirements

- **Classical algorithms**: 1-4 KB keys, small signatures
- **Post-quantum algorithms**: 1-100 KB keys, variable signature sizes
- **Runtime memory**: 50-500 MB depending on operations

## 🔒 Security Considerations

### Algorithm Status

- **Classical algorithms**: Vulnerable to quantum attacks
- **Post-quantum algorithms**: Standardized by NIST (2024)
- **Hybrid approaches**: Defense-in-depth strategy recommended

### Implementation Notes

- This is a **demonstration/research platform**, not production-ready
- Uses **simulation** for algorithms where liboqs is unavailable
- Focus on **educational value** and **migration planning**
- For production use, employ **certified implementations**

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```
   Error importing modules: No module named 'oqs'
   ```
   **Solution**: The suite falls back to simulation mode. No action needed for demonstration purposes.

2. **Port Binding Errors**:
   ```
   OSError: [WinError 10048] Only one usage of each socket address
   ```
   **Solution**: Ports are automatically selected. If issues persist, restart the application.

3. **Performance Issues**:
   ```
   Benchmark taking too long...
   ```
   **Solution**: Use `--quick` flag or run specific demos instead of all.

### Debug Mode

Enable verbose output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Run tests: `python -m pytest` (if test suite available)

### Adding New Algorithms

1. Extend the appropriate enum (e.g., `CryptoAlgorithm`)
2. Implement the algorithm interface
3. Add to benchmarking suite
4. Update documentation

### Reporting Issues

Please include:
- Python version
- Operating system
- Error messages
- Steps to reproduce
- Expected vs. actual behavior

## 📚 References

### Standards and Specifications

- [NIST Post-Quantum Cryptography Standards (2024)](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [RFC 8446 - TLS 1.3](https://tools.ietf.org/html/rfc8446)
- [NIST SP 800-208 - Recommendation for Stateful Hash-Based Signature Schemes](https://doi.org/10.6028/NIST.SP.800-208)

### Academic Papers

- Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing
- Regev, O. (2005). On lattices, learning with errors, random linear codes, and cryptography
- Bernstein, D. J., et al. (2019). Classic McEliece: conservative code-based cryptography

### Implementation References

- [liboqs - Open Quantum Safe](https://github.com/open-quantum-safe/liboqs)
- [PQClean - Clean implementations of post-quantum cryptography](https://github.com/PQClean/PQClean)
- [Kyber Reference Implementation](https://pq-crystals.org/kyber/)

## 📝 License

This project is provided for educational and research purposes. See individual algorithm implementations for their specific licensing terms.

## 🙏 Acknowledgments

- NIST Post-Quantum Cryptography Standardization Project
- Open Quantum Safe Project
- Academic researchers in post-quantum cryptography
- Python cryptographic community

## 📞 Support

For questions, suggestions, or collaboration:

- **Educational use**: Refer to documentation and code comments
- **Research applications**: Review benchmarking methodology
- **Enterprise migration**: Consult migration strategy documentation

---

**Disclaimer**: This software is for educational and research purposes only. Do not use in production environments without proper security review and certified implementations.
