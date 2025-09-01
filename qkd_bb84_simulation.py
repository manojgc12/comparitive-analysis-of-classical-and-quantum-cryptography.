"""
Quantum Key Distribution (QKD) BB84 Protocol Simulation
Comprehensive simulation including noise, eavesdropping, and distance effects
"""

import numpy as np
import random
import secrets
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

# Try to import qiskit for quantum circuit simulation
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Note: Qiskit not available, using classical simulation")

class PolarizationBasis(Enum):
    """Photon polarization bases"""
    RECTILINEAR = "+"  # 0° and 90°
    DIAGONAL = "×"     # 45° and 135°

class PhotonPolarization(Enum):
    """Specific photon polarizations"""
    HORIZONTAL = "→"   # 0° (bit 0 in rectilinear)
    VERTICAL = "↑"     # 90° (bit 1 in rectilinear)
    DIAGONAL_45 = "↗"  # 45° (bit 0 in diagonal)
    DIAGONAL_135 = "↖" # 135° (bit 1 in diagonal)

@dataclass
class Photon:
    """Individual photon with polarization"""
    bit_value: int  # 0 or 1
    polarization: PhotonPolarization
    basis: PolarizationBasis
    detected: bool = True
    measurement_basis: Optional[PolarizationBasis] = None
    measured_bit: Optional[int] = None

@dataclass
class ChannelParameters:
    """Quantum channel parameters"""
    distance_km: float = 50.0
    fiber_loss_db_per_km: float = 0.2  # Typical fiber loss
    detector_efficiency: float = 0.8   # Detector quantum efficiency
    dark_count_rate: float = 1e-6      # Dark count probability per detection window
    background_noise: float = 0.01     # Background photon noise
    timing_jitter_ps: float = 100.0    # Timing jitter in picoseconds

@dataclass
class EavesdropperConfig:
    """Eavesdropper (Eve) configuration"""
    intercept_probability: float = 0.5  # Probability of intercepting each photon
    measurement_strategy: str = "random"  # "random", "optimal", "basis_matching"
    resend_probability: float = 1.0     # Probability of resending after measurement

@dataclass
class BB84Result:
    """Results of BB84 protocol execution"""
    raw_key_length: int
    sifted_key_length: int
    final_key_length: int
    quantum_bit_error_rate: float
    key_generation_rate: float  # bits per second
    detected_eavesdropping: bool
    channel_parameters: ChannelParameters
    protocol_efficiency: float
    execution_time: float

class QuantumChannel:
    """Simulates quantum channel with realistic imperfections"""
    
    def __init__(self, params: ChannelParameters):
        self.params = params
        
        # Calculate distance-dependent loss
        self.transmission_probability = 10**(-params.fiber_loss_db_per_km * params.distance_km / 10)
        
        print(f"Quantum channel initialized:")
        print(f"  Distance: {params.distance_km} km")
        print(f"  Transmission probability: {self.transmission_probability:.4f}")
        print(f"  Detector efficiency: {params.detector_efficiency}")
    
    def transmit_photon(self, photon: Photon) -> Optional[Photon]:
        """Transmit a photon through the quantum channel"""
        # Fiber loss
        if random.random() > self.transmission_probability:
            photon.detected = False
            return None
        
        # Detector efficiency
        if random.random() > self.params.detector_efficiency:
            photon.detected = False
            return None
        
        # Dark counts (false detections)
        if random.random() < self.params.dark_count_rate:
            # Generate random dark count photon
            dark_photon = Photon(
                bit_value=random.randint(0, 1),
                polarization=random.choice(list(PhotonPolarization)),
                basis=random.choice(list(PolarizationBasis)),
                detected=True
            )
            return dark_photon
        
        # Background noise can flip polarization
        if random.random() < self.params.background_noise:
            # Randomly flip the bit
            photon.bit_value = 1 - photon.bit_value
            photon.polarization = self._get_polarization(photon.bit_value, photon.basis)
        
        return photon
    
    def _get_polarization(self, bit: int, basis: PolarizationBasis) -> PhotonPolarization:
        """Get polarization for bit value and basis"""
        if basis == PolarizationBasis.RECTILINEAR:
            return PhotonPolarization.HORIZONTAL if bit == 0 else PhotonPolarization.VERTICAL
        else:  # DIAGONAL
            return PhotonPolarization.DIAGONAL_45 if bit == 0 else PhotonPolarization.DIAGONAL_135

class Eavesdropper:
    """Simulates an eavesdropper (Eve) attacking the quantum channel"""
    
    def __init__(self, config: EavesdropperConfig):
        self.config = config
        self.intercepted_photons = []
        self.measurement_statistics = {"correct_basis": 0, "wrong_basis": 0}
    
    def intercept_photon(self, photon: Photon) -> Optional[Photon]:
        """Intercept and measure a photon, then potentially resend"""
        if random.random() > self.config.intercept_probability:
            return photon  # Don't intercept
        
        # Choose measurement basis based on strategy
        if self.config.measurement_strategy == "random":
            eve_basis = random.choice(list(PolarizationBasis))
        elif self.config.measurement_strategy == "optimal":
            # Try to guess the most likely basis (simplified)
            eve_basis = PolarizationBasis.RECTILINEAR  # Assume rectilinear is more common
        else:  # basis_matching - perfect knowledge (unrealistic)
            eve_basis = photon.basis
        
        # Measure the photon
        measured_bit = self._measure_photon(photon, eve_basis)
        
        # Record statistics
        if eve_basis == photon.basis:
            self.measurement_statistics["correct_basis"] += 1
        else:
            self.measurement_statistics["wrong_basis"] += 1
        
        # Store intercepted photon information
        self.intercepted_photons.append({
            "original_bit": photon.bit_value,
            "original_basis": photon.basis,
            "measurement_basis": eve_basis,
            "measured_bit": measured_bit
        })
        
        # Resend photon if configured to do so
        if random.random() <= self.config.resend_probability:
            # Create new photon based on Eve's measurement
            new_polarization = self._get_polarization(measured_bit, eve_basis)
            resent_photon = Photon(
                bit_value=measured_bit,
                polarization=new_polarization,
                basis=eve_basis,
                detected=True
            )
            return resent_photon
        else:
            return None  # Eve absorbed the photon
    
    def _measure_photon(self, photon: Photon, measurement_basis: PolarizationBasis) -> int:
        """Measure photon in specified basis"""
        if photon.basis == measurement_basis:
            # Correct basis - get the actual bit value
            return photon.bit_value
        else:
            # Wrong basis - random result
            return random.randint(0, 1)
    
    def _get_polarization(self, bit: int, basis: PolarizationBasis) -> PhotonPolarization:
        """Get polarization for bit value and basis"""
        if basis == PolarizationBasis.RECTILINEAR:
            return PhotonPolarization.HORIZONTAL if bit == 0 else PhotonPolarization.VERTICAL
        else:  # DIAGONAL
            return PhotonPolarization.DIAGONAL_45 if bit == 0 else PhotonPolarization.DIAGONAL_135

class BB84Protocol:
    """Complete BB84 Quantum Key Distribution protocol implementation"""
    
    def __init__(self, channel: QuantumChannel, eavesdropper: Optional[Eavesdropper] = None):
        self.channel = channel
        self.eavesdropper = eavesdropper
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bits = []
        self.bob_bases = []
        self.sifted_key = []
        self.final_key = []
        
        # Protocol parameters
        self.error_correction_efficiency = 1.2  # Shannon limit multiplier
        self.privacy_amplification_factor = 2   # Conservative factor
    
    def generate_random_bits(self, length: int) -> List[int]:
        """Generate cryptographically random bits"""
        return [secrets.randbits(1) for _ in range(length)]
    
    def generate_random_bases(self, length: int) -> List[PolarizationBasis]:
        """Generate random polarization bases"""
        return [secrets.choice(list(PolarizationBasis)) for _ in range(length)]
    
    def alice_prepare_photons(self, key_length: int) -> List[Photon]:
        """Alice prepares photons according to BB84 protocol"""
        self.alice_bits = self.generate_random_bits(key_length)
        self.alice_bases = self.generate_random_bases(key_length)
        
        photons = []
        for bit, basis in zip(self.alice_bits, self.alice_bases):
            if basis == PolarizationBasis.RECTILINEAR:
                polarization = PhotonPolarization.HORIZONTAL if bit == 0 else PhotonPolarization.VERTICAL
            else:  # DIAGONAL
                polarization = PhotonPolarization.DIAGONAL_45 if bit == 0 else PhotonPolarization.DIAGONAL_135
            
            photon = Photon(bit_value=bit, polarization=polarization, basis=basis)
            photons.append(photon)
        
        return photons
    
    def bob_receive_photons(self, photons: List[Photon]) -> List[Optional[Photon]]:
        """Bob receives and measures photons"""
        self.bob_bases = self.generate_random_bases(len(photons))
        received_photons = []
        self.bob_bits = []
        
        for i, photon in enumerate(photons):
            # Transmit through quantum channel
            received_photon = self.channel.transmit_photon(photon)
            
            if received_photon is None:
                received_photons.append(None)
                self.bob_bits.append(None)
                continue
            
            # Eavesdropper intercepts if present
            if self.eavesdropper:
                received_photon = self.eavesdropper.intercept_photon(received_photon)
                
                if received_photon is None:
                    received_photons.append(None)
                    self.bob_bits.append(None)
                    continue
            
            # Bob measures in random basis
            bob_basis = self.bob_bases[i]
            measured_bit = self._measure_photon_bob(received_photon, bob_basis)
            
            received_photon.measurement_basis = bob_basis
            received_photon.measured_bit = measured_bit
            
            received_photons.append(received_photon)
            self.bob_bits.append(measured_bit)
        
        return received_photons
    
    def _measure_photon_bob(self, photon: Photon, measurement_basis: PolarizationBasis) -> int:
        """Bob measures received photon"""
        if photon.basis == measurement_basis:
            # Matching basis - should get correct bit (ignoring noise for now)
            return photon.bit_value
        else:
            # Non-matching basis - random result
            return random.randint(0, 1)
    
    def basis_comparison_and_sifting(self) -> List[int]:
        """Alice and Bob compare bases and sift keys"""
        self.sifted_key = []
        
        for i in range(min(len(self.alice_bases), len(self.bob_bases))):
            if (self.bob_bits[i] is not None and 
                self.alice_bases[i] == self.bob_bases[i]):
                # Bases match - include in sifted key
                self.sifted_key.append(self.alice_bits[i])
        
        return self.sifted_key
    
    def estimate_quantum_bit_error_rate(self, sample_size: int = None) -> float:
        """Estimate QBER by comparing a sample of the sifted key"""
        if not self.sifted_key:
            return 0.0
        
        if sample_size is None:
            sample_size = min(len(self.sifted_key) // 4, 1000)  # Use up to 25% for estimation
        
        if sample_size >= len(self.sifted_key):
            # Not enough key material
            return 1.0
        
        # Randomly sample bits for error estimation
        sample_indices = random.sample(range(len(self.sifted_key)), sample_size)
        
        errors = 0
        alice_sample_bits = []
        bob_sample_bits = []
        
        # Get corresponding Alice and Bob bits for sampled positions
        sifted_position = 0
        for i in range(min(len(self.alice_bases), len(self.bob_bases))):
            if (self.bob_bits[i] is not None and 
                self.alice_bases[i] == self.bob_bases[i]):
                if sifted_position in sample_indices:
                    alice_sample_bits.append(self.alice_bits[i])
                    bob_sample_bits.append(self.bob_bits[i])
                sifted_position += 1
        
        # Compare sampled bits
        for alice_bit, bob_bit in zip(alice_sample_bits, bob_sample_bits):
            if alice_bit != bob_bit:
                errors += 1
        
        qber = errors / len(alice_sample_bits) if alice_sample_bits else 0.0
        
        # Remove sampled bits from sifted key
        remaining_key = []
        sifted_position = 0
        for i in range(min(len(self.alice_bases), len(self.bob_bases))):
            if (self.bob_bits[i] is not None and 
                self.alice_bases[i] == self.bob_bases[i]):
                if sifted_position not in sample_indices:
                    remaining_key.append(self.alice_bits[i])
                sifted_position += 1
        
        self.sifted_key = remaining_key
        return qber
    
    def error_correction_and_privacy_amplification(self, qber: float) -> List[int]:
        """Perform error correction and privacy amplification"""
        if not self.sifted_key:
            return []
        
        # Simplified error correction
        # In practice, this would use codes like LDPC or Cascade protocol
        error_correction_bits = int(len(self.sifted_key) * qber * self.error_correction_efficiency)
        
        # Privacy amplification to remove Eve's information
        # Assuming Eve has partial information based on interception
        privacy_amplification_bits = int(len(self.sifted_key) * 0.1)  # Conservative estimate
        
        if self.eavesdropper:
            # Additional privacy amplification based on Eve's potential knowledge
            intercept_rate = self.eavesdropper.config.intercept_probability
            privacy_amplification_bits += int(len(self.sifted_key) * intercept_rate * 0.5)
        
        # Calculate final key length
        total_reduction = error_correction_bits + privacy_amplification_bits
        final_key_length = max(0, len(self.sifted_key) - total_reduction)
        
        # Generate final key (simplified - just take first bits)
        self.final_key = self.sifted_key[:final_key_length]
        
        return self.final_key
    
    def run_protocol(self, key_length: int) -> BB84Result:
        """Run complete BB84 protocol"""
        start_time = datetime.now()
        
        print(f"\n=== Running BB84 Protocol ===")
        print(f"Requested key length: {key_length} bits")
        print(f"Channel distance: {self.channel.params.distance_km} km")
        print(f"Eavesdropper present: {self.eavesdropper is not None}")
        
        # Step 1: Alice prepares and sends photons
        photons = self.alice_prepare_photons(key_length)
        print(f"Alice prepared {len(photons)} photons")
        
        # Step 2: Bob receives and measures photons
        received_photons = self.bob_receive_photons(photons)
        detected_count = sum(1 for p in received_photons if p is not None)
        print(f"Bob detected {detected_count}/{len(photons)} photons ({detected_count/len(photons)*100:.1f}%)")
        
        # Step 3: Basis comparison and key sifting
        sifted_key = self.basis_comparison_and_sifting()
        print(f"Sifted key length: {len(sifted_key)} bits")
        
        # Step 4: Estimate QBER
        qber = self.estimate_quantum_bit_error_rate()
        print(f"Quantum Bit Error Rate (QBER): {qber*100:.2f}%")
        
        # Security check
        qber_threshold = 0.11  # Theoretical maximum for BB84 security
        detected_eavesdropping = qber > qber_threshold
        
        if detected_eavesdropping:
            print(f"⚠ SECURITY ALERT: QBER exceeds threshold ({qber_threshold*100:.1f}%)")
            print("  Possible eavesdropping detected - aborting key generation")
            final_key = []
        else:
            # Step 5: Error correction and privacy amplification
            final_key = self.error_correction_and_privacy_amplification(qber)
            print(f"Final secure key length: {len(final_key)} bits")
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Calculate key generation rate
        key_rate = len(final_key) / execution_time if execution_time > 0 else 0
        
        # Calculate protocol efficiency
        protocol_efficiency = len(final_key) / key_length if key_length > 0 else 0
        
        result = BB84Result(
            raw_key_length=key_length,
            sifted_key_length=len(sifted_key),
            final_key_length=len(final_key),
            quantum_bit_error_rate=qber,
            key_generation_rate=key_rate,
            detected_eavesdropping=detected_eavesdropping,
            channel_parameters=self.channel.params,
            protocol_efficiency=protocol_efficiency,
            execution_time=execution_time
        )
        
        print(f"Protocol efficiency: {protocol_efficiency*100:.1f}%")
        print(f"Key generation rate: {key_rate:.0f} bits/second")
        
        return result

class BB84Analyzer:
    """Analyzer for BB84 protocol results and security"""
    
    def __init__(self):
        self.results_history = []
    
    def add_result(self, result: BB84Result):
        """Add result to analysis history"""
        self.results_history.append(result)
    
    def analyze_distance_effects(self, distances: List[float], 
                                key_length: int = 10000) -> Dict[str, Any]:
        """Analyze effect of distance on BB84 performance"""
        print("\n=== Distance Effect Analysis ===")
        
        results = {}
        for distance in distances:
            print(f"\nTesting distance: {distance} km")
            
            # Create channel parameters for this distance
            channel_params = ChannelParameters(
                distance_km=distance,
                fiber_loss_db_per_km=0.2,
                detector_efficiency=0.8
            )
            
            channel = QuantumChannel(channel_params)
            protocol = BB84Protocol(channel)
            
            result = protocol.run_protocol(key_length)
            results[distance] = result
        
        return results
    
    def analyze_eavesdropping_detection(self, intercept_rates: List[float],
                                      key_length: int = 10000) -> Dict[str, Any]:
        """Analyze eavesdropping detection capabilities"""
        print("\n=== Eavesdropping Detection Analysis ===")
        
        results = {}
        
        # Standard channel parameters
        channel_params = ChannelParameters(distance_km=50.0)
        
        for intercept_rate in intercept_rates:
            print(f"\nTesting intercept rate: {intercept_rate*100:.0f}%")
            
            channel = QuantumChannel(channel_params)
            
            if intercept_rate > 0:
                eve_config = EavesdropperConfig(intercept_probability=intercept_rate)
                eavesdropper = Eavesdropper(eve_config)
            else:
                eavesdropper = None
            
            protocol = BB84Protocol(channel, eavesdropper)
            result = protocol.run_protocol(key_length)
            
            results[intercept_rate] = result
            
            if eavesdropper:
                print(f"  Eve's statistics: {eavesdropper.measurement_statistics}")
        
        return results
    
    def analyze_channel_noise_effects(self, noise_levels: List[float],
                                    key_length: int = 10000) -> Dict[str, Any]:
        """Analyze effect of channel noise on protocol"""
        print("\n=== Channel Noise Analysis ===")
        
        results = {}
        
        for noise_level in noise_levels:
            print(f"\nTesting noise level: {noise_level*100:.1f}%")
            
            channel_params = ChannelParameters(
                distance_km=50.0,
                background_noise=noise_level
            )
            
            channel = QuantumChannel(channel_params)
            protocol = BB84Protocol(channel)
            
            result = protocol.run_protocol(key_length)
            results[noise_level] = result
        
        return results
    
    def generate_analysis_report(self, output_file: str = "bb84_analysis_report.json"):
        """Generate comprehensive analysis report"""
        if not self.results_history:
            print("No results to analyze")
            return
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_experiments": len(self.results_history),
            "summary_statistics": self._calculate_summary_stats(),
            "security_analysis": self._analyze_security(),
            "performance_analysis": self._analyze_performance()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Analysis report saved to: {output_file}")
        return report
    
    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not self.results_history:
            return {}
        
        qber_values = [r.quantum_bit_error_rate for r in self.results_history]
        efficiency_values = [r.protocol_efficiency for r in self.results_history]
        key_rates = [r.key_generation_rate for r in self.results_history]
        
        return {
            "average_qber": np.mean(qber_values),
            "min_qber": np.min(qber_values),
            "max_qber": np.max(qber_values),
            "average_efficiency": np.mean(efficiency_values),
            "min_efficiency": np.min(efficiency_values),
            "max_efficiency": np.max(efficiency_values),
            "average_key_rate": np.mean(key_rates),
            "min_key_rate": np.min(key_rates),
            "max_key_rate": np.max(key_rates)
        }
    
    def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security aspects"""
        total_experiments = len(self.results_history)
        eavesdropping_detected = sum(1 for r in self.results_history if r.detected_eavesdropping)
        
        return {
            "eavesdropping_detection_rate": eavesdropping_detected / total_experiments,
            "secure_key_generation_rate": (total_experiments - eavesdropping_detected) / total_experiments,
            "qber_threshold": 0.11,
            "experiments_above_threshold": eavesdropping_detected
        }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        final_key_lengths = [r.final_key_length for r in self.results_history]
        execution_times = [r.execution_time for r in self.results_history]
        
        return {
            "average_final_key_length": np.mean(final_key_lengths),
            "average_execution_time": np.mean(execution_times),
            "key_length_std": np.std(final_key_lengths),
            "execution_time_std": np.std(execution_times)
        }
    
    def plot_distance_analysis(self, distance_results: Dict[float, BB84Result], 
                              save_path: str = "distance_analysis.png"):
        """Plot distance analysis results"""
        distances = list(distance_results.keys())
        efficiencies = [result.protocol_efficiency for result in distance_results.values()]
        qber_values = [result.quantum_bit_error_rate for result in distance_results.values()]
        key_rates = [result.key_generation_rate for result in distance_results.values()]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Protocol efficiency vs distance
        ax1.plot(distances, efficiencies, 'b-o')
        ax1.set_xlabel('Distance (km)')
        ax1.set_ylabel('Protocol Efficiency')
        ax1.set_title('BB84 Efficiency vs Distance')
        ax1.grid(True)
        
        # QBER vs distance
        ax2.plot(distances, qber_values, 'r-o')
        ax2.axhline(y=0.11, color='r', linestyle='--', label='Security Threshold')
        ax2.set_xlabel('Distance (km)')
        ax2.set_ylabel('QBER')
        ax2.set_title('Quantum Bit Error Rate vs Distance')
        ax2.legend()
        ax2.grid(True)
        
        # Key generation rate vs distance
        ax3.plot(distances, key_rates, 'g-o')
        ax3.set_xlabel('Distance (km)')
        ax3.set_ylabel('Key Rate (bits/s)')
        ax3.set_title('Key Generation Rate vs Distance')
        ax3.grid(True)
        
        # Combined view
        ax4_twin = ax4.twinx()
        line1 = ax4.plot(distances, efficiencies, 'b-o', label='Efficiency')
        line2 = ax4_twin.plot(distances, qber_values, 'r-s', label='QBER')
        
        ax4.set_xlabel('Distance (km)')
        ax4.set_ylabel('Protocol Efficiency', color='b')
        ax4_twin.set_ylabel('QBER', color='r')
        ax4.set_title('Efficiency and QBER vs Distance')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, loc='center right')
        ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Distance analysis plot saved to: {save_path}")

# Example usage and comprehensive testing
if __name__ == "__main__":
    print("=== Quantum Key Distribution BB84 Protocol Simulation ===\n")
    
    # Initialize analyzer
    analyzer = BB84Analyzer()
    
    # Demo 1: Basic BB84 Protocol
    print("1. Basic BB84 Protocol Demonstration")
    print("-" * 50)
    
    channel_params = ChannelParameters(
        distance_km=50.0,
        fiber_loss_db_per_km=0.2,
        detector_efficiency=0.8,
        background_noise=0.02
    )
    
    channel = QuantumChannel(channel_params)
    protocol = BB84Protocol(channel)
    
    result = protocol.run_protocol(key_length=10000)
    analyzer.add_result(result)
    
    print(f"\nBasic Protocol Results:")
    print(f"  Final key length: {result.final_key_length} bits")
    print(f"  Protocol efficiency: {result.protocol_efficiency*100:.1f}%")
    print(f"  QBER: {result.quantum_bit_error_rate*100:.2f}%")
    print(f"  Key generation rate: {result.key_generation_rate:.0f} bits/s")
    
    # Demo 2: Eavesdropping Detection
    print("\n\n2. Eavesdropping Detection Demonstration")
    print("-" * 50)
    
    # Test with eavesdropper
    eve_config = EavesdropperConfig(
        intercept_probability=0.3,  # Eve intercepts 30% of photons
        measurement_strategy="random"
    )
    
    eavesdropper = Eavesdropper(eve_config)
    protocol_with_eve = BB84Protocol(channel, eavesdropper)
    
    result_with_eve = protocol_with_eve.run_protocol(key_length=10000)
    analyzer.add_result(result_with_eve)
    
    print(f"\nWith Eavesdropper (30% intercept rate):")
    print(f"  QBER: {result_with_eve.quantum_bit_error_rate*100:.2f}%")
    print(f"  Eavesdropping detected: {result_with_eve.detected_eavesdropping}")
    print(f"  Final key length: {result_with_eve.final_key_length} bits")
    print(f"  Eve intercepted {len(eavesdropper.intercepted_photons)} photons")
    
    # Demo 3: Distance Analysis
    print("\n\n3. Distance Effect Analysis")
    print("-" * 50)
    
    distances = [10, 25, 50, 75, 100, 150, 200]
    distance_results = analyzer.analyze_distance_effects(distances, key_length=5000)
    
    # Add distance results to analyzer
    for result in distance_results.values():
        analyzer.add_result(result)
    
    # Demo 4: Eavesdropping Detection Analysis
    print("\n\n4. Eavesdropping Detection Analysis")
    print("-" * 50)
    
    intercept_rates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    eavesdrop_results = analyzer.analyze_eavesdropping_detection(intercept_rates, key_length=5000)
    
    print("\nEavesdropping Detection Summary:")
    print("Intercept Rate | QBER   | Detected | Key Length")
    print("-" * 50)
    for rate, result in eavesdrop_results.items():
        detected = "YES" if result.detected_eavesdropping else "NO"
        print(f"{rate*100:10.0f}%   | {result.quantum_bit_error_rate*100:5.1f}% | {detected:8} | {result.final_key_length:6} bits")
    
    # Add eavesdropping results to analyzer
    for result in eavesdrop_results.values():
        analyzer.add_result(result)
    
    # Demo 5: Channel Noise Analysis
    print("\n\n5. Channel Noise Analysis")
    print("-" * 50)
    
    noise_levels = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    noise_results = analyzer.analyze_channel_noise_effects(noise_levels, key_length=5000)
    
    # Add noise results to analyzer
    for result in noise_results.values():
        analyzer.add_result(result)
    
    # Generate comprehensive analysis
    try:
        # Plot distance analysis
        analyzer.plot_distance_analysis(distance_results)
        
        # Generate analysis report
        report = analyzer.generate_analysis_report()
        
        print("\n\n=== Comprehensive Analysis Summary ===")
        print(f"Total experiments: {report['total_experiments']}")
        print(f"Average QBER: {report['summary_statistics']['average_qber']*100:.2f}%")
        print(f"Average efficiency: {report['summary_statistics']['average_efficiency']*100:.1f}%")
        print(f"Average key rate: {report['summary_statistics']['average_key_rate']:.0f} bits/s")
        print(f"Eavesdropping detection rate: {report['security_analysis']['eavesdropping_detection_rate']*100:.1f}%")
        
    except Exception as e:
        print(f"Visualization error (expected without matplotlib): {e}")
    
    print("\n=== BB84 QKD Security Guarantees vs Post-Quantum Cryptography ===")
    print("\nBB84 QKD Advantages:")
    print("✓ Information-theoretic security (unconditional)")
    print("✓ Detects eavesdropping through quantum mechanics")
    print("✓ Forward secrecy guaranteed by quantum physics")
    print("✓ Secure against future quantum computers")
    
    print("\nBB84 QKD Limitations:")
    print("✗ Requires specialized hardware and infrastructure")
    print("✗ Limited transmission distance (~200 km over fiber)")
    print("✗ Low key generation rates")
    print("✗ Vulnerable to implementation flaws")
    print("✗ No authentication mechanism built-in")
    
    print("\nPost-Quantum Cryptography Advantages:")
    print("✓ Works on existing classical infrastructure")
    print("✓ High throughput and low latency")
    print("✓ Established mathematical foundations")
    print("✓ Can provide authentication and key exchange")
    print("✓ Cost-effective deployment")
    
    print("\nPost-Quantum Cryptography Limitations:")
    print("✗ Security based on computational assumptions")
    print("✗ Larger key/signature sizes than classical crypto")
    print("✗ Newer algorithms with less cryptanalysis history")
    print("✗ No inherent detection of attacks")
    
    print("\n=== Conclusion ===")
    print("Both QKD and Post-Quantum Cryptography play important roles:")
    print("• QKD: Ultimate security for high-value, low-bandwidth applications")
    print("• PQ Crypto: Practical quantum-safe protection for general use")
    print("• Hybrid approaches may provide the best of both worlds")
