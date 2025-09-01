"""
Migration Strategy and Threat Analysis Tools
Comprehensive tools for analyzing and planning post-quantum cryptography migration
"""

import json
import csv
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import secrets
import os

# Import our crypto modules for analysis
from quantum_signatures import SignatureAlgorithm
from hybrid_tls import CryptoAlgorithm

class ThreatLevel(Enum):
    """Threat assessment levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class AssetSensitivity(Enum):
    """Data/asset sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class QuantumThreatTimeline(Enum):
    """Estimated quantum threat timeline"""
    IMMEDIATE = "immediate"      # 0-2 years
    SHORT_TERM = "short_term"    # 2-5 years
    MEDIUM_TERM = "medium_term"  # 5-10 years
    LONG_TERM = "long_term"      # 10+ years

class MigrationPhase(Enum):
    """Migration phases"""
    PLANNING = "planning"
    PILOT = "pilot"
    ROLLOUT = "rollout"
    COMPLETION = "completion"
    MAINTENANCE = "maintenance"

@dataclass
class CryptographicAsset:
    """Represents a cryptographic asset in the organization"""
    asset_id: str
    name: str
    asset_type: str  # "certificate", "key", "algorithm", "protocol", "application"
    current_algorithm: str
    key_size: int
    sensitivity_level: AssetSensitivity
    criticality: ThreatLevel
    location: str  # "on_premise", "cloud", "hybrid"
    owner: str
    last_updated: datetime
    expiry_date: Optional[datetime] = None
    dependencies: List[str] = None  # List of dependent asset IDs
    quantum_vulnerable: bool = True
    migration_priority: int = 1  # 1 = highest priority
    estimated_migration_effort: str = "unknown"  # "low", "medium", "high"
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ThreatScenario:
    """Quantum threat scenario"""
    scenario_id: str
    name: str
    description: str
    threat_level: ThreatLevel
    probability: float  # 0.0 to 1.0
    timeline: QuantumThreatTimeline
    affected_algorithms: List[str]
    impact_description: str
    mitigation_strategies: List[str]

@dataclass
class MigrationPlan:
    """Migration plan for an asset or group of assets"""
    plan_id: str
    asset_ids: List[str]
    current_state: str
    target_state: str
    migration_phase: MigrationPhase
    start_date: datetime
    target_completion: datetime
    estimated_cost: float
    required_resources: List[str]
    risks: List[str]
    dependencies: List[str]
    success_criteria: List[str]
    rollback_plan: str

@dataclass 
class RiskAssessment:
    """Risk assessment result"""
    asset_id: str
    current_risk_score: float  # 0.0 to 10.0
    residual_risk_score: float  # After migration
    risk_factors: List[str]
    recommended_actions: List[str]
    timeline_recommendation: QuantumThreatTimeline

class QuantumThreatAnalyzer:
    """Analyzes quantum threats and vulnerabilities"""
    
    def __init__(self):
        self.quantum_vulnerable_algorithms = {
            # Asymmetric cryptography
            "RSA": {"key_sizes": [1024, 2048, 3072, 4096], "threat_level": ThreatLevel.CRITICAL},
            "DSA": {"key_sizes": [1024, 2048, 3072], "threat_level": ThreatLevel.CRITICAL},
            "ECDSA": {"key_sizes": [256, 384, 521], "threat_level": ThreatLevel.CRITICAL},
            "ECDH": {"key_sizes": [256, 384, 521], "threat_level": ThreatLevel.CRITICAL},
            "DH": {"key_sizes": [1024, 2048, 3072, 4096], "threat_level": ThreatLevel.CRITICAL},
            "ElGamal": {"key_sizes": [1024, 2048, 3072, 4096], "threat_level": ThreatLevel.CRITICAL},
            
            # Symmetric cryptography (affected by Grover's algorithm)
            "AES": {"key_sizes": [128, 192, 256], "threat_level": ThreatLevel.MEDIUM},
            "3DES": {"key_sizes": [168], "threat_level": ThreatLevel.HIGH},
            "ChaCha20": {"key_sizes": [256], "threat_level": ThreatLevel.MEDIUM},
            
            # Hash functions (affected by Grover's algorithm)
            "SHA1": {"key_sizes": [160], "threat_level": ThreatLevel.HIGH},
            "SHA2": {"key_sizes": [224, 256, 384, 512], "threat_level": ThreatLevel.MEDIUM},
            "SHA3": {"key_sizes": [224, 256, 384, 512], "threat_level": ThreatLevel.MEDIUM},
            "MD5": {"key_sizes": [128], "threat_level": ThreatLevel.CRITICAL}
        }
        
        self.quantum_safe_algorithms = {
            # NIST PQC Standards
            "CRYSTALS-Kyber": {"type": "KEM", "security_levels": [1, 3, 5]},
            "CRYSTALS-Dilithium": {"type": "Signature", "security_levels": [2, 3, 5]},
            "FALCON": {"type": "Signature", "security_levels": [1, 5]},
            "SPHINCS+": {"type": "Signature", "security_levels": [1, 3, 5]},
            
            # Other candidates
            "NTRU": {"type": "KEM", "security_levels": [1, 3, 5]},
            "SABER": {"type": "KEM", "security_levels": [1, 3, 5]},
            "FrodoKEM": {"type": "KEM", "security_levels": [1, 3, 5]},
            "McEliece": {"type": "KEM", "security_levels": [1, 3, 5]}
        }
        
        # Threat scenarios
        self.threat_scenarios = [
            ThreatScenario(
                scenario_id="QC_BREAKTHROUGH",
                name="Quantum Computing Breakthrough",
                description="Sudden breakthrough in quantum computing making current crypto vulnerable",
                threat_level=ThreatLevel.CRITICAL,
                probability=0.1,
                timeline=QuantumThreatTimeline.SHORT_TERM,
                affected_algorithms=["RSA", "ECDSA", "ECDH", "DSA", "DH"],
                impact_description="Complete compromise of public key cryptography",
                mitigation_strategies=["Immediate PQC deployment", "Emergency crypto-agility activation"]
            ),
            ThreatScenario(
                scenario_id="GRADUAL_IMPROVEMENT",
                name="Gradual Quantum Computing Improvement",
                description="Steady improvements in quantum computing over next decade",
                threat_level=ThreatLevel.HIGH,
                probability=0.7,
                timeline=QuantumThreatTimeline.MEDIUM_TERM,
                affected_algorithms=["RSA", "ECDSA", "ECDH", "DSA", "DH"],
                impact_description="Progressive weakening of current cryptography",
                mitigation_strategies=["Phased PQC migration", "Hybrid approaches", "Key size increases"]
            ),
            ThreatScenario(
                scenario_id="HARVEST_NOW_DECRYPT_LATER",
                name="Harvest Now, Decrypt Later Attacks",
                description="Adversaries collecting encrypted data for future quantum decryption",
                threat_level=ThreatLevel.HIGH,
                probability=0.9,
                timeline=QuantumThreatTimeline.IMMEDIATE,
                affected_algorithms=["RSA", "ECDSA", "ECDH", "DSA", "DH"],
                impact_description="Long-term confidential data at risk",
                mitigation_strategies=["Immediate hybrid crypto", "Data re-encryption", "Forward secrecy"]
            ),
            ThreatScenario(
                scenario_id="PARTIAL_CRYPTANALYSIS",
                name="Partial Cryptanalytic Breakthrough",
                description="Classical cryptanalytic breakthrough affecting specific algorithms",
                threat_level=ThreatLevel.MEDIUM,
                probability=0.3,
                timeline=QuantumThreatTimeline.SHORT_TERM,
                affected_algorithms=["RSA", "ECDSA"],
                impact_description="Specific algorithms become vulnerable",
                mitigation_strategies=["Algorithm diversification", "Key size increases", "Algorithm agility"]
            )
        ]
    
    def assess_algorithm_vulnerability(self, algorithm: str, key_size: int) -> Dict[str, Any]:
        """Assess vulnerability of a specific algorithm and key size"""
        algorithm_upper = algorithm.upper()
        
        if algorithm_upper not in self.quantum_vulnerable_algorithms:
            # Assume unknown algorithms are potentially vulnerable
            return {
                "vulnerable": True,
                "threat_level": ThreatLevel.MEDIUM,
                "confidence": "low",
                "recommendation": "Evaluate algorithm quantum resistance"
            }
        
        alg_info = self.quantum_vulnerable_algorithms[algorithm_upper]
        threat_level = alg_info["threat_level"]
        
        # Special handling for symmetric crypto (Grover's algorithm effect)
        if algorithm_upper in ["AES", "CHACHA20"]:
            if key_size >= 256:
                effective_security = key_size // 2  # Grover's algorithm effect
                if effective_security >= 128:
                    threat_level = ThreatLevel.MEDIUM
                else:
                    threat_level = ThreatLevel.HIGH
            else:
                threat_level = ThreatLevel.HIGH
        
        # Hash functions
        elif algorithm_upper in ["SHA1", "SHA2", "SHA3", "MD5"]:
            if algorithm_upper == "SHA1" or algorithm_upper == "MD5":
                threat_level = ThreatLevel.CRITICAL
            else:
                effective_security = key_size // 2
                if effective_security >= 128:
                    threat_level = ThreatLevel.MEDIUM
                else:
                    threat_level = ThreatLevel.HIGH
        
        return {
            "vulnerable": True,
            "threat_level": threat_level,
            "confidence": "high",
            "grover_affected": algorithm_upper in ["AES", "CHACHA20", "SHA1", "SHA2", "SHA3"],
            "shor_affected": algorithm_upper in ["RSA", "DSA", "ECDSA", "ECDH", "DH", "ELGAMAL"],
            "recommendation": self._get_migration_recommendation(algorithm_upper, key_size, threat_level)
        }
    
    def _get_migration_recommendation(self, algorithm: str, key_size: int, threat_level: ThreatLevel) -> str:
        """Get migration recommendation for algorithm"""
        if threat_level == ThreatLevel.CRITICAL:
            return "Immediate migration required"
        elif threat_level == ThreatLevel.HIGH:
            return "High priority migration within 1-2 years"
        elif threat_level == ThreatLevel.MEDIUM:
            if algorithm in ["AES", "CHACHA20"] and key_size >= 256:
                return "Monitor and consider key size increase to 256+ bits"
            else:
                return "Medium priority migration within 3-5 years"
        else:
            return "Low priority, monitor for developments"
    
    def calculate_risk_score(self, asset: CryptographicAsset) -> float:
        """Calculate risk score for a cryptographic asset"""
        base_score = 0.0
        
        # Algorithm vulnerability (40% weight)
        vulnerability = self.assess_algorithm_vulnerability(asset.current_algorithm, asset.key_size)
        threat_weights = {
            ThreatLevel.CRITICAL: 10.0,
            ThreatLevel.HIGH: 7.5,
            ThreatLevel.MEDIUM: 5.0,
            ThreatLevel.LOW: 2.5
        }
        base_score += threat_weights[vulnerability["threat_level"]] * 0.4
        
        # Asset sensitivity (25% weight)
        sensitivity_weights = {
            AssetSensitivity.TOP_SECRET: 10.0,
            AssetSensitivity.SECRET: 8.0,
            AssetSensitivity.CONFIDENTIAL: 6.0,
            AssetSensitivity.INTERNAL: 4.0,
            AssetSensitivity.PUBLIC: 2.0
        }
        base_score += sensitivity_weights[asset.sensitivity_level] * 0.25
        
        # Asset criticality (20% weight)
        criticality_weights = {
            ThreatLevel.CRITICAL: 10.0,
            ThreatLevel.HIGH: 7.5,
            ThreatLevel.MEDIUM: 5.0,
            ThreatLevel.LOW: 2.5
        }
        base_score += criticality_weights[asset.criticality] * 0.2
        
        # Age/expiry factor (10% weight)
        if asset.expiry_date:
            days_to_expiry = (asset.expiry_date - datetime.now()).days
            if days_to_expiry < 365:  # Less than 1 year
                age_factor = 8.0
            elif days_to_expiry < 730:  # Less than 2 years
                age_factor = 6.0
            else:
                age_factor = 4.0
        else:
            # No expiry date - consider age from last update
            days_since_update = (datetime.now() - asset.last_updated).days
            if days_since_update > 1095:  # More than 3 years
                age_factor = 8.0
            elif days_since_update > 730:  # More than 2 years
                age_factor = 6.0
            else:
                age_factor = 4.0
        
        base_score += age_factor * 0.1
        
        # Location factor (5% weight)
        location_weights = {
            "cloud": 7.0,      # Higher exposure
            "hybrid": 6.0,
            "on_premise": 4.0  # Lower exposure
        }
        base_score += location_weights.get(asset.location, 5.0) * 0.05
        
        return min(base_score, 10.0)  # Cap at 10.0

class AssetInventoryManager:
    """Manages cryptographic asset inventory"""
    
    def __init__(self):
        self.assets: Dict[str, CryptographicAsset] = {}
        self.threat_analyzer = QuantumThreatAnalyzer()
    
    def add_asset(self, asset: CryptographicAsset):
        """Add a cryptographic asset to inventory"""
        self.assets[asset.asset_id] = asset
    
    def remove_asset(self, asset_id: str):
        """Remove asset from inventory"""
        if asset_id in self.assets:
            del self.assets[asset_id]
    
    def get_asset(self, asset_id: str) -> Optional[CryptographicAsset]:
        """Get asset by ID"""
        return self.assets.get(asset_id)
    
    def list_assets_by_criteria(self, **criteria) -> List[CryptographicAsset]:
        """List assets matching criteria"""
        matching_assets = []
        
        for asset in self.assets.values():
            match = True
            for key, value in criteria.items():
                if hasattr(asset, key):
                    if getattr(asset, key) != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                matching_assets.append(asset)
        
        return matching_assets
    
    def get_vulnerable_assets(self) -> List[CryptographicAsset]:
        """Get all quantum-vulnerable assets"""
        return [asset for asset in self.assets.values() if asset.quantum_vulnerable]
    
    def generate_risk_assessment_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk assessment report"""
        risk_assessments = []
        
        for asset in self.assets.values():
            risk_score = self.threat_analyzer.calculate_risk_score(asset)
            vulnerability = self.threat_analyzer.assess_algorithm_vulnerability(
                asset.current_algorithm, asset.key_size
            )
            
            assessment = RiskAssessment(
                asset_id=asset.asset_id,
                current_risk_score=risk_score,
                residual_risk_score=risk_score * 0.1,  # Assume 90% risk reduction after migration
                risk_factors=[
                    f"Algorithm: {asset.current_algorithm}",
                    f"Key size: {asset.key_size}",
                    f"Sensitivity: {asset.sensitivity_level.value}",
                    f"Location: {asset.location}"
                ],
                recommended_actions=[vulnerability["recommendation"]],
                timeline_recommendation=self._get_timeline_recommendation(risk_score)
            )
            
            risk_assessments.append(assessment)
        
        # Sort by risk score
        risk_assessments.sort(key=lambda x: x.current_risk_score, reverse=True)
        
        # Generate summary statistics
        risk_scores = [ra.current_risk_score for ra in risk_assessments]
        high_risk_count = len([rs for rs in risk_scores if rs >= 7.5])
        medium_risk_count = len([rs for rs in risk_scores if 5.0 <= rs < 7.5])
        low_risk_count = len([rs for rs in risk_scores if rs < 5.0])
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_assets": len(self.assets),
            "risk_distribution": {
                "high_risk": high_risk_count,
                "medium_risk": medium_risk_count,
                "low_risk": low_risk_count
            },
            "average_risk_score": sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            "risk_assessments": [asdict(ra) for ra in risk_assessments],
            "recommendations": self._generate_overall_recommendations(risk_assessments)
        }
    
    def _get_timeline_recommendation(self, risk_score: float) -> QuantumThreatTimeline:
        """Get timeline recommendation based on risk score"""
        if risk_score >= 8.5:
            return QuantumThreatTimeline.IMMEDIATE
        elif risk_score >= 7.0:
            return QuantumThreatTimeline.SHORT_TERM
        elif risk_score >= 5.0:
            return QuantumThreatTimeline.MEDIUM_TERM
        else:
            return QuantumThreatTimeline.LONG_TERM
    
    def _generate_overall_recommendations(self, risk_assessments: List[RiskAssessment]) -> List[str]:
        """Generate overall recommendations based on risk assessments"""
        recommendations = []
        
        high_risk_count = len([ra for ra in risk_assessments if ra.current_risk_score >= 7.5])
        total_assets = len(risk_assessments)
        
        if high_risk_count > total_assets * 0.5:
            recommendations.append("Immediate organization-wide PQC migration planning required")
            recommendations.append("Consider emergency crypto-agility measures")
        elif high_risk_count > total_assets * 0.25:
            recommendations.append("High priority PQC migration program needed")
            recommendations.append("Focus on highest risk assets first")
        else:
            recommendations.append("Planned PQC migration over 3-5 year timeline")
        
        recommendations.append("Implement crypto-agility framework")
        recommendations.append("Establish quantum threat monitoring")
        recommendations.append("Develop incident response procedures for quantum threats")
        
        return recommendations
    
    def export_inventory_csv(self, filename: str):
        """Export asset inventory to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'asset_id', 'name', 'asset_type', 'current_algorithm', 'key_size',
                'sensitivity_level', 'criticality', 'location', 'owner', 'last_updated',
                'expiry_date', 'quantum_vulnerable', 'migration_priority'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for asset in self.assets.values():
                row = asdict(asset)
                # Convert datetime objects to strings
                row['last_updated'] = asset.last_updated.isoformat()
                row['expiry_date'] = asset.expiry_date.isoformat() if asset.expiry_date else ''
                row['sensitivity_level'] = asset.sensitivity_level.value
                row['criticality'] = asset.criticality.value
                row['dependencies'] = ','.join(asset.dependencies)
                writer.writerow(row)
        
        print(f"Asset inventory exported to: {filename}")

class MigrationPlanner:
    """Plans and manages post-quantum cryptography migration"""
    
    def __init__(self, inventory_manager: AssetInventoryManager):
        self.inventory_manager = inventory_manager
        self.migration_plans: Dict[str, MigrationPlan] = {}
        
        # Algorithm mapping for migration
        self.migration_mappings = {
            "RSA": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"],
            "ECDSA": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"],
            "DSA": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"],
            "ECDH": ["CRYSTALS-Kyber", "NTRU", "SABER"],
            "DH": ["CRYSTALS-Kyber", "NTRU", "SABER"],
            "RSA_OAEP": ["CRYSTALS-Kyber", "NTRU", "SABER"]  # For encryption
        }
    
    def create_migration_plan(self, asset_ids: List[str], 
                            target_completion_days: int = 365) -> str:
        """Create migration plan for specified assets"""
        plan_id = f"PLAN_{secrets.token_hex(8).upper()}"
        
        # Analyze assets
        assets = [self.inventory_manager.get_asset(aid) for aid in asset_ids if self.inventory_manager.get_asset(aid)]
        
        if not assets:
            raise ValueError("No valid assets found for migration plan")
        
        # Determine current and target states
        current_algorithms = list(set(asset.current_algorithm for asset in assets))
        target_algorithms = self._recommend_target_algorithms(current_algorithms)
        
        # Calculate estimated cost and effort
        total_cost = self._estimate_migration_cost(assets)
        required_resources = self._identify_required_resources(assets)
        
        # Identify risks and dependencies
        risks = self._identify_migration_risks(assets)
        dependencies = self._analyze_dependencies(assets)
        
        migration_plan = MigrationPlan(
            plan_id=plan_id,
            asset_ids=asset_ids,
            current_state=", ".join(current_algorithms),
            target_state=", ".join(target_algorithms),
            migration_phase=MigrationPhase.PLANNING,
            start_date=datetime.now() + timedelta(days=30),  # 30 day planning buffer
            target_completion=datetime.now() + timedelta(days=target_completion_days),
            estimated_cost=total_cost,
            required_resources=required_resources,
            risks=risks,
            dependencies=dependencies,
            success_criteria=[
                "All assets migrated to quantum-safe algorithms",
                "No degradation in system performance",
                "Security validation completed",
                "Rollback capability verified"
            ],
            rollback_plan="Maintain parallel classical systems until migration validation complete"
        )
        
        self.migration_plans[plan_id] = migration_plan
        return plan_id
    
    def _recommend_target_algorithms(self, current_algorithms: List[str]) -> List[str]:
        """Recommend target algorithms for migration"""
        target_algorithms = set()
        
        for algorithm in current_algorithms:
            algorithm_upper = algorithm.upper()
            if algorithm_upper in self.migration_mappings:
                # Use first (preferred) algorithm from mapping
                target_algorithms.add(self.migration_mappings[algorithm_upper][0])
            else:
                # Default recommendation
                if algorithm_upper in ["RSA", "ECDSA", "DSA"]:
                    target_algorithms.add("CRYSTALS-Dilithium")
                elif algorithm_upper in ["ECDH", "DH"]:
                    target_algorithms.add("CRYSTALS-Kyber")
                else:
                    target_algorithms.add("CRYSTALS-Kyber")  # Default KEM
        
        return list(target_algorithms)
    
    def _estimate_migration_cost(self, assets: List[CryptographicAsset]) -> float:
        """Estimate migration cost based on assets"""
        base_costs = {
            "certificate": 500.0,      # Certificate replacement
            "key": 200.0,             # Key generation and distribution
            "algorithm": 2000.0,      # Algorithm implementation
            "protocol": 5000.0,       # Protocol updates
            "application": 10000.0    # Application modifications
        }
        
        effort_multipliers = {
            "low": 1.0,
            "medium": 2.0,
            "high": 4.0,
            "unknown": 3.0
        }
        
        total_cost = 0.0
        
        for asset in assets:
            base_cost = base_costs.get(asset.asset_type.lower(), 1000.0)
            effort_multiplier = effort_multipliers.get(asset.estimated_migration_effort, 3.0)
            
            # Add complexity factor based on dependencies
            complexity_factor = 1.0 + (len(asset.dependencies) * 0.2)
            
            asset_cost = base_cost * effort_multiplier * complexity_factor
            total_cost += asset_cost
        
        return total_cost
    
    def _identify_required_resources(self, assets: List[CryptographicAsset]) -> List[str]:
        """Identify required resources for migration"""
        resources = set()
        
        for asset in assets:
            if asset.asset_type.lower() == "application":
                resources.add("Software Development Team")
                resources.add("Application Security Specialist")
            elif asset.asset_type.lower() == "certificate":
                resources.add("PKI Administrator")
                resources.add("Certificate Authority Access")
            elif asset.asset_type.lower() == "protocol":
                resources.add("Network Security Engineer")
                resources.add("Protocol Specialist")
            
            if asset.location == "cloud":
                resources.add("Cloud Security Specialist")
            elif asset.location == "hybrid":
                resources.add("Hybrid Infrastructure Specialist")
            
            resources.add("Quantum Cryptography Specialist")
            resources.add("Testing and Validation Team")
        
        return list(resources)
    
    def _identify_migration_risks(self, assets: List[CryptographicAsset]) -> List[str]:
        """Identify migration risks"""
        risks = [
            "Performance degradation due to larger key/signature sizes",
            "Compatibility issues with legacy systems",
            "Implementation vulnerabilities in new algorithms",
            "Increased computational overhead",
            "Key management complexity",
            "Rollback complexity if issues arise"
        ]
        
        # Add specific risks based on assets
        asset_types = set(asset.asset_type.lower() for asset in assets)
        
        if "application" in asset_types:
            risks.append("Application integration challenges")
            risks.append("User experience impact")
        
        if "protocol" in asset_types:
            risks.append("Protocol interoperability issues")
            risks.append("Network performance impact")
        
        if any(asset.criticality == ThreatLevel.CRITICAL for asset in assets):
            risks.append("Business continuity impact during migration")
            risks.append("Security vulnerabilities during transition")
        
        return risks
    
    def _analyze_dependencies(self, assets: List[CryptographicAsset]) -> List[str]:
        """Analyze migration dependencies"""
        dependencies = set()
        
        for asset in assets:
            dependencies.update(asset.dependencies)
            
            # Add implicit dependencies based on asset type
            if asset.asset_type.lower() == "application":
                dependencies.add("Underlying cryptographic libraries")
                dependencies.add("Operating system crypto support")
            elif asset.asset_type.lower() == "certificate":
                dependencies.add("Certificate Authority infrastructure")
                dependencies.add("Certificate validation systems")
        
        return list(dependencies)
    
    def generate_migration_timeline(self, plan_id: str) -> Dict[str, Any]:
        """Generate detailed migration timeline"""
        if plan_id not in self.migration_plans:
            raise ValueError(f"Migration plan {plan_id} not found")
        
        plan = self.migration_plans[plan_id]
        duration_days = (plan.target_completion - plan.start_date).days
        
        # Define migration phases
        phases = [
            {"name": "Planning & Design", "duration_pct": 0.20, "phase": MigrationPhase.PLANNING},
            {"name": "Pilot Implementation", "duration_pct": 0.15, "phase": MigrationPhase.PILOT},
            {"name": "Main Rollout", "duration_pct": 0.50, "phase": MigrationPhase.ROLLOUT},
            {"name": "Completion & Validation", "duration_pct": 0.10, "phase": MigrationPhase.COMPLETION},
            {"name": "Maintenance & Monitoring", "duration_pct": 0.05, "phase": MigrationPhase.MAINTENANCE}
        ]
        
        timeline = []
        current_date = plan.start_date
        
        for phase in phases:
            phase_duration = int(duration_days * phase["duration_pct"])
            phase_end = current_date + timedelta(days=phase_duration)
            
            timeline.append({
                "phase_name": phase["name"],
                "phase_enum": phase["phase"],
                "start_date": current_date.isoformat(),
                "end_date": phase_end.isoformat(),
                "duration_days": phase_duration,
                "milestones": self._generate_phase_milestones(phase["phase"], phase_duration)
            })
            
            current_date = phase_end
        
        return {
            "plan_id": plan_id,
            "total_duration_days": duration_days,
            "timeline": timeline,
            "critical_path": self._identify_critical_path(plan),
            "resource_allocation": self._generate_resource_allocation(plan, timeline)
        }
    
    def _generate_phase_milestones(self, phase: MigrationPhase, duration: int) -> List[str]:
        """Generate milestones for a migration phase"""
        milestones = {
            MigrationPhase.PLANNING: [
                "Risk assessment completed",
                "Target algorithms selected",
                "Implementation plan approved",
                "Resource allocation confirmed"
            ],
            MigrationPhase.PILOT: [
                "Pilot environment setup",
                "Initial algorithm implementation",
                "Pilot testing completed",
                "Go/no-go decision made"
            ],
            MigrationPhase.ROLLOUT: [
                "Production deployment started",
                "50% of assets migrated",
                "Performance validation completed",
                "All assets migrated"
            ],
            MigrationPhase.COMPLETION: [
                "Security validation completed",
                "Documentation updated",
                "Training completed",
                "Migration signed off"
            ],
            MigrationPhase.MAINTENANCE: [
                "Monitoring systems in place",
                "Incident procedures established",
                "Performance baseline established",
                "Maintenance plan activated"
            ]
        }
        
        return milestones.get(phase, ["Phase milestone"])
    
    def _identify_critical_path(self, plan: MigrationPlan) -> List[str]:
        """Identify critical path items"""
        return [
            "Algorithm selection and validation",
            "Legacy system compatibility testing",
            "Performance impact assessment",
            "Security validation",
            "Rollback procedure verification"
        ]
    
    def _generate_resource_allocation(self, plan: MigrationPlan, timeline: List[Dict]) -> Dict[str, Any]:
        """Generate resource allocation across timeline"""
        allocation = {}
        
        for resource in plan.required_resources:
            allocation[resource] = []
            
            for phase in timeline:
                # Allocate different effort levels based on phase
                phase_enum = phase["phase_enum"]
                
                if resource == "Quantum Cryptography Specialist":
                    if phase_enum in [MigrationPhase.PLANNING, MigrationPhase.PILOT]:
                        effort = "high"
                    elif phase_enum == MigrationPhase.ROLLOUT:
                        effort = "medium"
                    else:
                        effort = "low"
                elif "Developer" in resource or "Engineer" in resource:
                    if phase_enum in [MigrationPhase.PILOT, MigrationPhase.ROLLOUT]:
                        effort = "high"
                    elif phase_enum == MigrationPhase.PLANNING:
                        effort = "medium"
                    else:
                        effort = "low"
                else:
                    effort = "medium"
                
                allocation[resource].append({
                    "phase": phase["phase_name"],
                    "effort_level": effort,
                    "duration_days": phase["duration_days"]
                })
        
        return allocation
    
    def export_migration_plan(self, plan_id: str, filename: str):
        """Export migration plan to JSON"""
        if plan_id not in self.migration_plans:
            raise ValueError(f"Migration plan {plan_id} not found")
        
        plan = self.migration_plans[plan_id]
        timeline = self.generate_migration_timeline(plan_id)
        
        export_data = {
            "migration_plan": asdict(plan),
            "timeline": timeline,
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Convert datetime objects to strings
        export_data["migration_plan"]["start_date"] = plan.start_date.isoformat()
        export_data["migration_plan"]["target_completion"] = plan.target_completion.isoformat()
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Migration plan exported to: {filename}")

class RegulationComplianceChecker:
    """Checks compliance with quantum-safe cryptography regulations"""
    
    def __init__(self):
        # Regulatory frameworks and their requirements
        self.regulatory_frameworks = {
            "NIST": {
                "name": "NIST Post-Quantum Cryptography Standards",
                "approved_algorithms": {
                    "KEM": ["CRYSTALS-Kyber"],
                    "Signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
                },
                "key_requirements": [
                    "Use NIST-approved post-quantum algorithms",
                    "Implement crypto-agility",
                    "Maintain security level equivalent to AES-128 or higher"
                ],
                "timeline": "Migrate by 2030"
            },
            "NSA_CNSS": {
                "name": "NSA Commercial National Security Algorithm Suite",
                "approved_algorithms": {
                    "KEM": ["CRYSTALS-Kyber"],
                    "Signature": ["CRYSTALS-Dilithium", "FALCON"]
                },
                "key_requirements": [
                    "Use NSA-approved algorithms for national security systems",
                    "Implement Suite B replacement",
                    "Maintain TOP SECRET capability"
                ],
                "timeline": "Migrate by 2033"
            },
            "EU_CYBERSEC": {
                "name": "EU Cybersecurity Act",
                "approved_algorithms": {
                    "KEM": ["CRYSTALS-Kyber", "NTRU", "SABER"],
                    "Signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
                },
                "key_requirements": [
                    "Comply with EU cybersecurity standards",
                    "Implement quantum-safe cryptography for critical infrastructure",
                    "Maintain GDPR compliance"
                ],
                "timeline": "Migrate by 2028"
            }
        }
    
    def check_compliance(self, assets: List[CryptographicAsset], 
                        framework: str = "NIST") -> Dict[str, Any]:
        """Check compliance with specified regulatory framework"""
        if framework not in self.regulatory_frameworks:
            raise ValueError(f"Unknown framework: {framework}")
        
        framework_info = self.regulatory_frameworks[framework]
        approved_algorithms = set()
        for alg_type in framework_info["approved_algorithms"].values():
            approved_algorithms.update(alg_type)
        
        compliant_assets = []
        non_compliant_assets = []
        
        for asset in assets:
            if asset.current_algorithm in approved_algorithms or not asset.quantum_vulnerable:
                compliant_assets.append(asset.asset_id)
            else:
                non_compliant_assets.append(asset.asset_id)
        
        compliance_rate = len(compliant_assets) / len(assets) if assets else 0
        
        return {
            "framework": framework,
            "framework_name": framework_info["name"],
            "compliance_rate": compliance_rate,
            "compliant_assets": compliant_assets,
            "non_compliant_assets": non_compliant_assets,
            "requirements": framework_info["key_requirements"],
            "migration_deadline": framework_info["timeline"],
            "approved_algorithms": framework_info["approved_algorithms"],
            "recommendations": self._generate_compliance_recommendations(
                non_compliant_assets, framework_info
            )
        }
    
    def _generate_compliance_recommendations(self, non_compliant_assets: List[str], 
                                          framework_info: Dict) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if non_compliant_assets:
            recommendations.extend([
                f"Migrate {len(non_compliant_assets)} non-compliant assets",
                "Prioritize migration based on asset criticality",
                "Implement approved post-quantum algorithms",
                "Establish compliance monitoring"
            ])
        
        recommendations.extend([
            "Implement crypto-agility framework",
            "Regular compliance audits",
            "Stay updated with regulatory changes",
            "Document compliance procedures"
        ])
        
        return recommendations

# Example usage and demonstration
if __name__ == "__main__":
    print("=== Post-Quantum Cryptography Migration Strategy & Threat Analysis ===\n")
    
    # Initialize components
    inventory_manager = AssetInventoryManager()
    migration_planner = MigrationPlanner(inventory_manager)
    compliance_checker = RegulationComplianceChecker()
    
    # Demo 1: Create sample asset inventory
    print("1. Creating Sample Asset Inventory")
    print("-" * 50)
    
    sample_assets = [
        CryptographicAsset(
            asset_id="WEB_TLS_CERT_001",
            name="Primary Web Server TLS Certificate",
            asset_type="certificate",
            current_algorithm="RSA",
            key_size=2048,
            sensitivity_level=AssetSensitivity.CONFIDENTIAL,
            criticality=ThreatLevel.HIGH,
            location="cloud",
            owner="IT Security Team",
            last_updated=datetime(2023, 1, 15),
            expiry_date=datetime(2025, 1, 15),
            migration_priority=1,
            estimated_migration_effort="medium"
        ),
        CryptographicAsset(
            asset_id="API_SIGNING_KEY_002",
            name="API Request Signing Key",
            asset_type="key",
            current_algorithm="ECDSA",
            key_size=256,
            sensitivity_level=AssetSensitivity.INTERNAL,
            criticality=ThreatLevel.MEDIUM,
            location="on_premise",
            owner="Development Team",
            last_updated=datetime(2022, 6, 10),
            migration_priority=2,
            estimated_migration_effort="high"
        ),
        CryptographicAsset(
            asset_id="DB_ENCRYPT_KEY_003",
            name="Database Encryption Key",
            asset_type="key",
            current_algorithm="AES",
            key_size=256,
            sensitivity_level=AssetSensitivity.SECRET,
            criticality=ThreatLevel.CRITICAL,
            location="on_premise",
            owner="Database Team",
            last_updated=datetime(2023, 8, 20),
            migration_priority=1,
            estimated_migration_effort="low",
            quantum_vulnerable=False  # AES-256 is quantum-resistant with larger key
        ),
        CryptographicAsset(
            asset_id="VPN_IPSEC_004",
            name="VPN IPSec Configuration",
            asset_type="protocol",
            current_algorithm="ECDH",
            key_size=384,
            sensitivity_level=AssetSensitivity.CONFIDENTIAL,
            criticality=ThreatLevel.HIGH,
            location="hybrid",
            owner="Network Team",
            last_updated=datetime(2021, 12, 5),
            migration_priority=1,
            estimated_migration_effort="high"
        ),
        CryptographicAsset(
            asset_id="LEGACY_APP_005",
            name="Legacy Financial Application",
            asset_type="application",
            current_algorithm="RSA",
            key_size=1024,
            sensitivity_level=AssetSensitivity.SECRET,
            criticality=ThreatLevel.CRITICAL,
            location="on_premise",
            owner="Finance Team",
            last_updated=datetime(2020, 3, 12),
            migration_priority=1,
            estimated_migration_effort="high"
        )
    ]
    
    for asset in sample_assets:
        inventory_manager.add_asset(asset)
        print(f"✓ Added asset: {asset.name}")
    
    print(f"\nTotal assets in inventory: {len(inventory_manager.assets)}")
    
    # Demo 2: Risk Assessment
    print("\n\n2. Risk Assessment Analysis")
    print("-" * 50)
    
    risk_report = inventory_manager.generate_risk_assessment_report()
    
    print(f"Risk Distribution:")
    print(f"  High Risk (≥7.5):   {risk_report['risk_distribution']['high_risk']} assets")
    print(f"  Medium Risk (5-7.5): {risk_report['risk_distribution']['medium_risk']} assets")
    print(f"  Low Risk (<5):       {risk_report['risk_distribution']['low_risk']} assets")
    print(f"\nAverage Risk Score: {risk_report['average_risk_score']:.2f}/10.0")
    
    print("\nTop Risk Assets:")
    for i, assessment in enumerate(risk_report['risk_assessments'][:3]):
        asset = inventory_manager.get_asset(assessment['asset_id'])
        print(f"  {i+1}. {asset.name}: {assessment['current_risk_score']:.1f}/10.0")
        print(f"     Algorithm: {asset.current_algorithm}-{asset.key_size}")
        print(f"     Timeline: {assessment['timeline_recommendation']}")
    
    # Demo 3: Migration Planning
    print("\n\n3. Migration Planning")
    print("-" * 50)
    
    # Create migration plan for high-risk assets
    high_risk_assets = [
        ra['asset_id'] for ra in risk_report['risk_assessments'] 
        if ra['current_risk_score'] >= 7.0
    ]
    
    if high_risk_assets:
        plan_id = migration_planner.create_migration_plan(high_risk_assets, 730)  # 2 years
        print(f"✓ Created migration plan: {plan_id}")
        
        plan = migration_planner.migration_plans[plan_id]
        print(f"  Target completion: {plan.target_completion.strftime('%Y-%m-%d')}")
        print(f"  Estimated cost: ${plan.estimated_cost:,.0f}")
        print(f"  Assets to migrate: {len(plan.asset_ids)}")
        
        # Generate timeline
        timeline = migration_planner.generate_migration_timeline(plan_id)
        print(f"  Total duration: {timeline['total_duration_days']} days")
        print(f"  Phases: {len(timeline['timeline'])}")
        
        # Export migration plan
        plan_filename = f"migration_plan_{plan_id}.json"
        migration_planner.export_migration_plan(plan_id, plan_filename)
    
    # Demo 4: Compliance Checking
    print("\n\n4. Regulatory Compliance Analysis")
    print("-" * 50)
    
    frameworks = ["NIST", "NSA_CNSS", "EU_CYBERSEC"]
    
    for framework in frameworks:
        compliance = compliance_checker.check_compliance(
            list(inventory_manager.assets.values()), framework
        )
        
        print(f"\n{compliance['framework_name']}:")
        print(f"  Compliance Rate: {compliance['compliance_rate']*100:.1f}%")
        print(f"  Compliant Assets: {len(compliance['compliant_assets'])}")
        print(f"  Non-compliant Assets: {len(compliance['non_compliant_assets'])}")
        print(f"  Migration Deadline: {compliance['migration_deadline']}")
    
    # Demo 5: Threat Scenario Analysis
    print("\n\n5. Threat Scenario Analysis")
    print("-" * 50)
    
    threat_analyzer = QuantumThreatAnalyzer()
    
    print("Key Threat Scenarios:")
    for scenario in threat_analyzer.threat_scenarios:
        print(f"\n{scenario.name}:")
        print(f"  Threat Level: {scenario.threat_level.value.upper()}")
        print(f"  Probability: {scenario.probability*100:.0f}%")
        print(f"  Timeline: {scenario.timeline.value.replace('_', ' ').title()}")
        print(f"  Impact: {scenario.impact_description}")
        print(f"  Mitigation: {', '.join(scenario.mitigation_strategies[:2])}")
    
    # Demo 6: Export Reports
    print("\n\n6. Exporting Reports")
    print("-" * 50)
    
    # Export asset inventory
    inventory_filename = "crypto_asset_inventory.csv"
    inventory_manager.export_inventory_csv(inventory_filename)
    
    # Export risk assessment
    risk_filename = "risk_assessment_report.json"
    with open(risk_filename, 'w') as f:
        json.dump(risk_report, f, indent=2, default=str)
    print(f"✓ Risk assessment report saved: {risk_filename}")
    
    # Generate compliance report
    compliance_report = {}
    for framework in frameworks:
        compliance_report[framework] = compliance_checker.check_compliance(
            list(inventory_manager.assets.values()), framework
        )
    
    compliance_filename = "compliance_report.json"
    with open(compliance_filename, 'w') as f:
        json.dump(compliance_report, f, indent=2, default=str)
    print(f"✓ Compliance report saved: {compliance_filename}")
    
    print("\n\n=== Summary & Key Recommendations ===")
    print("1. Immediate Actions:")
    for recommendation in risk_report['recommendations'][:3]:
        print(f"   • {recommendation}")
    
    print("\n2. Migration Priorities:")
    print("   • Focus on RSA-1024 and other weak algorithms first")
    print("   • Prioritize high-sensitivity and critical assets")
    print("   • Implement hybrid approaches during transition")
    
    print("\n3. Long-term Strategy:")
    print("   • Establish crypto-agility framework")
    print("   • Regular threat assessment and monitoring")
    print("   • Continuous compliance validation")
    print("   • Incident response procedures for quantum threats")
    
    print("\n=== Migration Strategy Complete ===")
    print("All reports and plans have been generated and exported.")
    print("Review the exported files for detailed analysis and planning.")
