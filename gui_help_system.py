#!/usr/bin/env python3
"""
Quantum-Safe Cryptography Suite - Help and Documentation System
Comprehensive help system for the GUI application

This module provides:
1. Algorithm descriptions and references
2. Usage instructions and tutorials
3. Troubleshooting guides
4. Performance optimization tips
5. Migration strategies
6. Security considerations
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Any
import webbrowser
import json
from datetime import datetime

class HelpSystem:
    """Comprehensive help and documentation system"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.help_window = None
        
        # Help content database
        self.help_content = self.load_help_content()
    
    def load_help_content(self) -> Dict[str, Any]:
        """Load help content from data structures"""
        return {
            "algorithms": {
                "Classical Algorithms": {
                    "RSA": {
                        "description": "RSA (Rivest-Shamir-Adleman) is a widely used public-key cryptosystem.",
                        "key_sizes": ["1024-bit (deprecated)", "2048-bit (current)", "3072-bit (future)"],
                        "security_level": "Vulnerable to quantum attacks via Shor's algorithm",
                        "performance": "Slow key generation, moderate signing/verification",
                        "use_cases": ["Legacy systems", "Backwards compatibility"],
                        "migration": "Migrate to post-quantum signatures like Dilithium"
                    },
                    "ECDSA": {
                        "description": "Elliptic Curve Digital Signature Algorithm using elliptic curve cryptography.",
                        "key_sizes": ["P-256 (128-bit security)", "P-384 (192-bit security)", "P-521 (256-bit security)"],
                        "security_level": "Vulnerable to quantum attacks via Shor's algorithm",
                        "performance": "Fast signing and verification, small signatures",
                        "use_cases": ["TLS certificates", "Code signing", "Mobile applications"],
                        "migration": "Consider hybrid approach with post-quantum algorithms"
                    },
                    "Ed25519": {
                        "description": "Edwards curve signature scheme with high performance and security.",
                        "key_sizes": ["32-byte keys", "64-byte signatures"],
                        "security_level": "Strong classical security, quantum vulnerable",
                        "performance": "Very fast signing and verification",
                        "use_cases": ["SSH keys", "Git commits", "High-performance applications"],
                        "migration": "Excellent performance for transition period"
                    }
                },
                "Post-Quantum Algorithms": {
                    "Dilithium": {
                        "description": "Lattice-based signature scheme standardized by NIST.",
                        "variants": ["Dilithium2 (128-bit)", "Dilithium3 (192-bit)", "Dilithium5 (256-bit)"],
                        "security_level": "Quantum-resistant based on lattice problems",
                        "performance": "Moderate signing, fast verification, large signatures",
                        "key_sizes": {
                            "Dilithium2": "Public: 1312 bytes, Private: 2528 bytes, Signature: 2420 bytes",
                            "Dilithium3": "Public: 1952 bytes, Private: 4000 bytes, Signature: 3293 bytes",
                            "Dilithium5": "Public: 2592 bytes, Private: 4864 bytes, Signature: 4595 bytes"
                        },
                        "use_cases": ["General-purpose digital signatures", "Certificate authorities", "Document signing"],
                        "advantages": ["NIST standardized", "Good performance balance", "Strong security"],
                        "disadvantages": ["Large key/signature sizes", "Newer algorithm"]
                    },
                    "Falcon": {
                        "description": "Compact lattice-based signature scheme with small signatures.",
                        "variants": ["Falcon-512 (128-bit)", "Falcon-1024 (256-bit)"],
                        "security_level": "Quantum-resistant based on NTRU lattices",
                        "performance": "Fast signing and verification, small signatures",
                        "key_sizes": {
                            "Falcon-512": "Public: 897 bytes, Private: 1281 bytes, Signature: 666 bytes",
                            "Falcon-1024": "Public: 1793 bytes, Private: 2305 bytes, Signature: 1280 bytes"
                        },
                        "use_cases": ["Constrained environments", "IoT devices", "Real-time applications"],
                        "advantages": ["Compact signatures", "Good performance", "NIST standardized"],
                        "disadvantages": ["Complex implementation", "Floating-point operations"]
                    },
                    "SPHINCS+": {
                        "description": "Hash-based signature scheme with conservative security assumptions.",
                        "variants": ["128f", "192f", "256f (security levels)", "s/f (size/speed trade-offs)"],
                        "security_level": "Quantum-resistant based on hash functions",
                        "performance": "Slow signing, fast verification, very large signatures",
                        "key_sizes": {
                            "SPHINCS+-SHA256-128f": "Public: 32 bytes, Private: 64 bytes, Signature: 17088 bytes",
                            "SPHINCS+-SHA256-192f": "Public: 48 bytes, Private: 96 bytes, Signature: 35664 bytes",
                            "SPHINCS+-SHA256-256f": "Public: 64 bytes, Private: 128 bytes, Signature: 49856 bytes"
                        },
                        "use_cases": ["Ultra-high security", "Long-term signatures", "Conservative deployments"],
                        "advantages": ["Conservative security", "Small keys", "Hash-based"],
                        "disadvantages": ["Extremely large signatures", "Slow signing"]
                    },
                    "Kyber": {
                        "description": "Lattice-based key encapsulation mechanism for TLS and VPNs.",
                        "variants": ["Kyber-512 (128-bit)", "Kyber-768 (192-bit)", "Kyber-1024 (256-bit)"],
                        "security_level": "Quantum-resistant based on Module-LWE",
                        "performance": "Fast key generation and encapsulation",
                        "key_sizes": {
                            "Kyber-512": "Public: 800 bytes, Private: 1632 bytes, Ciphertext: 768 bytes",
                            "Kyber-768": "Public: 1184 bytes, Private: 2400 bytes, Ciphertext: 1088 bytes",
                            "Kyber-1024": "Public: 1568 bytes, Private: 3168 bytes, Ciphertext: 1568 bytes"
                        },
                        "use_cases": ["TLS handshakes", "VPN key exchange", "Secure messaging"],
                        "advantages": ["NIST standardized", "Good performance", "Reasonable sizes"],
                        "disadvantages": ["Larger than classical", "Newer algorithm"]
                    }
                }
            },
            "usage": {
                "Getting Started": {
                    "installation": [
                        "1. Ensure Python 3.8 or higher is installed",
                        "2. Install required packages: pip install -r requirements.txt",
                        "3. Run the GUI launcher: python run_gui.py",
                        "4. Or run directly: python gui_application.py"
                    ],
                    "first_steps": [
                        "1. Start with the Dashboard tab to see available demonstrations",
                        "2. Select a demonstration by clicking its button",
                        "3. Configure algorithms in the Configuration tab if needed",
                        "4. Click 'Run Selected Demo' to start",
                        "5. View results in the Results tab"
                    ],
                    "navigation": [
                        "• Dashboard: Select and run demonstrations",
                        "• Results: View formatted results with charts and tables",
                        "• Configuration: Adjust algorithm settings",
                        "• Logs: Monitor application activity"
                    ]
                },
                "Demonstrations": {
                    "hybrid_tls": {
                        "name": "Hybrid TLS Handshakes",
                        "description": "Demonstrates TLS 1.3 key exchange with classical and post-quantum algorithms",
                        "configurations": [
                            "Classical X25519: Traditional elliptic curve",
                            "Hybrid X25519+Kyber768: Combined classical and post-quantum",
                            "Triple Hybrid: Multiple algorithm combination",
                            "Post-Quantum Only: Pure post-quantum approach"
                        ],
                        "metrics": ["Handshake duration", "Key sizes", "Protocol efficiency", "Algorithm combinations"],
                        "use_cases": ["TLS migration planning", "Performance analysis", "Security evaluation"]
                    },
                    "signatures": {
                        "name": "Digital Signatures",
                        "description": "Compares classical and post-quantum digital signature algorithms",
                        "algorithms": ["RSA-PSS", "ECDSA", "Ed25519", "Dilithium", "Falcon", "SPHINCS+"],
                        "metrics": ["Key generation time", "Signing time", "Verification time", "Key sizes", "Signature sizes"],
                        "use_cases": ["Certificate migration", "Code signing", "Document authentication"]
                    },
                    "benchmark": {
                        "name": "Performance Benchmark",
                        "description": "Comprehensive performance testing of all algorithms",
                        "categories": ["Key generation", "Signing/verification", "TLS handshakes"],
                        "configuration": "Adjust iterations in Configuration tab",
                        "output": ["Performance rankings", "Statistical analysis", "Comparison charts"]
                    },
                    "qkd": {
                        "name": "Quantum Key Distribution",
                        "description": "BB84 protocol simulation with eavesdropping detection",
                        "scenarios": ["Secure channel", "Eavesdropping detection", "Distance analysis"],
                        "metrics": ["Key generation rate", "Quantum bit error rate", "Security analysis"],
                        "physics": "Simulates quantum mechanical properties of photons"
                    },
                    "migration": {
                        "name": "Migration Strategy",
                        "description": "Enterprise cryptographic asset migration planning",
                        "features": ["Asset inventory", "Risk assessment", "Compliance checking", "Cost estimation"],
                        "frameworks": ["NIST", "NSA CNSS", "EU Cybersecurity"],
                        "output": ["Migration timeline", "Risk reports", "Compliance status"]
                    }
                }
            },
            "troubleshooting": {
                "Common Issues": {
                    "import_errors": {
                        "issue": "ImportError: No module named 'oqs'",
                        "cause": "Open Quantum Safe library not installed",
                        "solution": [
                            "This is normal - the suite uses simulation mode when OQS is unavailable",
                            "For real OQS algorithms: pip install oqs-python",
                            "Note: OQS may require system dependencies on some platforms"
                        ],
                        "workaround": "Simulation mode provides realistic performance estimates"
                    },
                    "gui_freezing": {
                        "issue": "GUI becomes unresponsive during demonstrations",
                        "cause": "Long-running demonstrations block the GUI thread",
                        "solution": [
                            "This is expected behavior for complex demonstrations",
                            "Use Quick mode for faster execution",
                            "Monitor progress in the status bar",
                            "Check the Logs tab for updates"
                        ],
                        "prevention": "Reduce benchmark iterations in Configuration"
                    },
                    "memory_issues": {
                        "issue": "High memory usage during benchmarks",
                        "cause": "Large-scale algorithm testing requires significant memory",
                        "solution": [
                            "Close other applications before running benchmarks",
                            "Use Quick mode for reduced memory usage",
                            "Run individual demonstrations instead of 'All'"
                        ],
                        "specifications": "Recommend 8GB RAM for full benchmark suite"
                    },
                    "chart_errors": {
                        "issue": "Charts not displaying or showing errors",
                        "cause": "Missing matplotlib or display issues",
                        "solution": [
                            "Ensure matplotlib is installed: pip install matplotlib",
                            "Update display drivers if running on Windows",
                            "Try switching between different result views",
                            "Export charts if viewing is problematic"
                        ]
                    }
                },
                "Performance Issues": {
                    "slow_demos": {
                        "issue": "Demonstrations take too long to complete",
                        "solutions": [
                            "Use Quick mode in Configuration tab",
                            "Reduce benchmark iterations (default: 25, try 10)",
                            "Run specific demos instead of all at once",
                            "Ensure no other CPU-intensive applications are running"
                        ]
                    },
                    "optimization": {
                        "title": "Performance Optimization Tips",
                        "tips": [
                            "Close unnecessary applications before benchmarking",
                            "Use SSD storage for faster file I/O",
                            "Ensure adequate RAM (8GB+ recommended)",
                            "Run on dedicated CPU cores when possible",
                            "Update Python and cryptographic libraries",
                            "Consider running in virtual environment"
                        ]
                    }
                }
            },
            "security": {
                "Algorithm Security": {
                    "classical_limitations": [
                        "RSA and ECDSA vulnerable to quantum attacks via Shor's algorithm",
                        "Current RSA 2048-bit provides ~112 bits of security",
                        "ECDSA P-256 provides ~128 bits of classical security",
                        "All classical algorithms will be broken by large quantum computers"
                    ],
                    "pq_advantages": [
                        "Post-quantum algorithms resist both classical and quantum attacks",
                        "Based on different mathematical problems (lattices, hashes, codes)",
                        "NIST standardization provides confidence in security",
                        "Hybrid approaches provide defense-in-depth"
                    ],
                    "security_levels": {
                        "Level 1": "128-bit classical security equivalent (AES-128)",
                        "Level 3": "192-bit classical security equivalent (AES-192)", 
                        "Level 5": "256-bit classical security equivalent (AES-256)"
                    }
                },
                "Migration Considerations": {
                    "timeline": [
                        "Start planning now - cryptoagility is key",
                        "NIST recommends beginning migration immediately",
                        "Large quantum computers may exist within 10-15 years",
                        "Legacy systems may require extended transition periods"
                    ],
                    "hybrid_strategy": [
                        "Use both classical and post-quantum algorithms",
                        "Provides protection against both current and future threats",
                        "Allows gradual migration and compatibility",
                        "Higher computational and bandwidth costs"
                    ],
                    "risk_assessment": [
                        "Identify all cryptographic assets in your organization",
                        "Assess sensitivity and exposure duration",
                        "Prioritize high-value, long-term sensitive data",
                        "Consider regulatory and compliance requirements"
                    ]
                }
            },
            "references": {
                "NIST Standards": {
                    "FIPS 203": "Module-Lattice-Based Key-Encapsulation Mechanism (Kyber)",
                    "FIPS 204": "Module-Lattice-Based Digital Signature Standard (Dilithium)",
                    "FIPS 205": "Stateless Hash-Based Digital Signature Standard (SPHINCS+)",
                    "SP 800-208": "Recommendation for Stateful Hash-Based Signature Schemes"
                },
                "Academic Papers": [
                    "Alagic et al. (2022): Status Report on the Third Round of the NIST Post-Quantum Cryptography Standardization Process",
                    "Bernstein et al. (2019): Classic McEliece: conservative code-based cryptography",
                    "Ducas et al. (2018): CRYSTALS-Dilithium: A Lattice-Based Digital Signature Scheme",
                    "Fouque et al. (2018): Falcon: Fast-Fourier Lattice-based Compact Signatures over NTRU"
                ],
                "Online Resources": [
                    "NIST Post-Quantum Cryptography: https://csrc.nist.gov/projects/post-quantum-cryptography",
                    "Open Quantum Safe: https://openquantumsafe.org/",
                    "PQClean: https://github.com/PQClean/PQClean",
                    "Quantum Computing Report: https://quantumcomputingreport.com/"
                ]
            }
        }
    
    def show_help(self, topic="overview"):
        """Show help window with specific topic"""
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.focus()
            return
        
        self.help_window = tk.Toplevel(self.parent if self.parent else None)
        self.help_window.title("Quantum-Safe Cryptography Suite - Help")
        self.help_window.geometry("1000x700")
        self.help_window.minsize(800, 600)
        
        # Create help interface
        self.create_help_interface()
        
        # Show specific topic if requested
        if topic != "overview":
            self.show_topic(topic)
    
    def create_help_interface(self):
        """Create the help system interface"""
        # Main container
        main_frame = ttk.Frame(self.help_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create paned window for navigation and content
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Navigation panel
        nav_frame = ttk.Frame(paned)
        paned.add(nav_frame, weight=1)
        
        # Content panel
        content_frame = ttk.Frame(paned)
        paned.add(content_frame, weight=3)
        
        # Create navigation tree
        self.create_navigation(nav_frame)
        
        # Create content area
        self.create_content_area(content_frame)
        
        # Create toolbar
        self.create_help_toolbar(main_frame)
    
    def create_navigation(self, parent):
        """Create navigation tree for help topics"""
        # Navigation header
        nav_header = ttk.Label(parent, text="Help Topics", font=('Segoe UI', 12, 'bold'))
        nav_header.pack(pady=(0, 10))
        
        # Tree view for navigation
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.nav_tree = ttk.Treeview(tree_frame)
        nav_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.nav_tree.yview)
        self.nav_tree.config(yscrollcommand=nav_scroll.set)
        
        self.nav_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        nav_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate navigation tree
        self.populate_navigation()
        
        # Bind selection event
        self.nav_tree.bind('<<TreeviewSelect>>', self.on_nav_selection)
    
    def populate_navigation(self):
        """Populate the navigation tree with help topics"""
        # Overview
        overview_id = self.nav_tree.insert('', tk.END, text="📖 Overview", open=True)
        self.nav_tree.insert(overview_id, tk.END, text="Getting Started", values=("usage", "Getting Started"))
        self.nav_tree.insert(overview_id, tk.END, text="Quick Tour", values=("overview", "quick_tour"))
        
        # Algorithms
        algo_id = self.nav_tree.insert('', tk.END, text="🔐 Algorithms", open=True)
        
        # Classical algorithms
        classical_id = self.nav_tree.insert(algo_id, tk.END, text="Classical Algorithms")
        for alg in ["RSA", "ECDSA", "Ed25519"]:
            self.nav_tree.insert(classical_id, tk.END, text=alg, values=("algorithms", f"Classical Algorithms.{alg}"))
        
        # Post-quantum algorithms  
        pq_id = self.nav_tree.insert(algo_id, tk.END, text="Post-Quantum Algorithms")
        for alg in ["Dilithium", "Falcon", "SPHINCS+", "Kyber"]:
            self.nav_tree.insert(pq_id, tk.END, text=alg, values=("algorithms", f"Post-Quantum Algorithms.{alg}"))
        
        # Demonstrations
        demo_id = self.nav_tree.insert('', tk.END, text="🧪 Demonstrations", open=True)
        demos = [
            ("Hybrid TLS", "hybrid_tls"),
            ("Digital Signatures", "signatures"), 
            ("Performance Benchmark", "benchmark"),
            ("QKD Simulation", "qkd"),
            ("Migration Strategy", "migration")
        ]
        for name, key in demos:
            self.nav_tree.insert(demo_id, tk.END, text=name, values=("usage", f"Demonstrations.{key}"))
        
        # Troubleshooting
        trouble_id = self.nav_tree.insert('', tk.END, text="🔧 Troubleshooting", open=True)
        self.nav_tree.insert(trouble_id, tk.END, text="Common Issues", values=("troubleshooting", "Common Issues"))
        self.nav_tree.insert(trouble_id, tk.END, text="Performance Issues", values=("troubleshooting", "Performance Issues"))
        
        # Security
        security_id = self.nav_tree.insert('', tk.END, text="🛡️ Security", open=True)
        self.nav_tree.insert(security_id, tk.END, text="Algorithm Security", values=("security", "Algorithm Security"))
        self.nav_tree.insert(security_id, tk.END, text="Migration Guide", values=("security", "Migration Considerations"))
        
        # References
        ref_id = self.nav_tree.insert('', tk.END, text="📚 References", open=True)
        self.nav_tree.insert(ref_id, tk.END, text="NIST Standards", values=("references", "NIST Standards"))
        self.nav_tree.insert(ref_id, tk.END, text="Academic Papers", values=("references", "Academic Papers"))
        self.nav_tree.insert(ref_id, tk.END, text="Online Resources", values=("references", "Online Resources"))
    
    def create_content_area(self, parent):
        """Create the main content display area"""
        # Content header
        self.content_header = ttk.Label(parent, text="Welcome to the Help System", 
                                       font=('Segoe UI', 14, 'bold'))
        self.content_header.pack(pady=(0, 10))
        
        # Content display
        content_container = ttk.Frame(parent)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        self.content_display = scrolledtext.ScrolledText(content_container, 
                                                       font=('Segoe UI', 11),
                                                       wrap=tk.WORD,
                                                       padx=20, pady=20)
        self.content_display.pack(fill=tk.BOTH, expand=True)
        
        # Show initial content
        self.show_overview()
    
    def create_help_toolbar(self, parent):
        """Create help system toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(10, 0))
        
        # Search functionality
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', self.search_help)
        
        ttk.Button(toolbar, text="🔍 Search", command=self.search_help).pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(toolbar, text="🏠 Overview", command=self.show_overview).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📋 Contents", command=self.show_contents).pack(side=tk.LEFT, padx=5)
        
        # External links
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(toolbar, text="🌐 NIST PQC", command=self.open_nist_pqc).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔗 Open Quantum Safe", command=self.open_oqs).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(toolbar, text="❌ Close", command=self.help_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def on_nav_selection(self, event):
        """Handle navigation tree selection"""
        selection = self.nav_tree.selection()
        if selection:
            item = selection[0]
            values = self.nav_tree.item(item, 'values')
            if values and len(values) >= 2:
                category, topic = values[0], values[1]
                self.show_topic_content(category, topic)
    
    def show_topic_content(self, category: str, topic: str):
        """Show content for a specific topic"""
        self.content_display.delete('1.0', tk.END)
        
        try:
            # Navigate to the topic in help content
            content = self.help_content.get(category, {})
            
            if '.' in topic:
                # Nested topic (e.g., "Classical Algorithms.RSA")
                parts = topic.split('.')
                for part in parts:
                    content = content.get(part, {})
            else:
                content = content.get(topic, {})
            
            if isinstance(content, dict):
                self.display_structured_content(content, topic)
            else:
                self.content_display.insert(tk.END, str(content))
                
        except Exception as e:
            self.content_display.insert(tk.END, f"Error loading content: {e}")
        
        # Update header
        self.content_header.config(text=topic.replace('.', ' - '))
    
    def display_structured_content(self, content: Dict, title: str):
        """Display structured content dictionary"""
        self.content_display.insert(tk.END, f"{title.upper()}\n", "header")
        self.content_display.insert(tk.END, "=" * len(title) + "\n\n")
        
        for key, value in content.items():
            if key == "description":
                self.content_display.insert(tk.END, f"{value}\n\n")
            elif isinstance(value, list):
                self.content_display.insert(tk.END, f"{key.title()}:\n", "subheader")
                for item in value:
                    self.content_display.insert(tk.END, f"  • {item}\n")
                self.content_display.insert(tk.END, "\n")
            elif isinstance(value, dict):
                self.content_display.insert(tk.END, f"{key.title()}:\n", "subheader")
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (list, str)):
                        self.content_display.insert(tk.END, f"  {subkey}: {subvalue}\n")
                    else:
                        self.content_display.insert(tk.END, f"  {subkey}: {str(subvalue)}\n")
                self.content_display.insert(tk.END, "\n")
            else:
                self.content_display.insert(tk.END, f"{key.title()}: {value}\n\n")
        
        # Configure text tags for formatting
        self.content_display.tag_configure("header", font=('Segoe UI', 14, 'bold'))
        self.content_display.tag_configure("subheader", font=('Segoe UI', 12, 'bold'))
    
    def show_overview(self):
        """Show help system overview"""
        self.content_header.config(text="Quantum-Safe Cryptography Suite - Help Overview")
        self.content_display.delete('1.0', tk.END)
        
        overview_text = """Welcome to the Quantum-Safe Cryptography Suite Help System

This comprehensive help system provides detailed information about:

🔐 CRYPTOGRAPHIC ALGORITHMS
Detailed descriptions of both classical and post-quantum cryptographic algorithms, including their security properties, performance characteristics, and use cases.

🧪 DEMONSTRATIONS  
Step-by-step guides for using each demonstration in the suite, including configuration options and result interpretation.

🔧 TROUBLESHOOTING
Common issues and their solutions, performance optimization tips, and system requirements.

🛡️ SECURITY CONSIDERATIONS
Important security information about quantum threats, migration strategies, and algorithm selection criteria.

📚 REFERENCES
Links to official standards, academic papers, and additional resources for further learning.

GETTING STARTED
1. Use the navigation tree on the left to browse topics
2. Click on any topic to view detailed information  
3. Use the search function to find specific information
4. Visit external links for official documentation

NAVIGATION TIPS
• Click the triangles to expand/collapse sections
• Use the toolbar buttons for quick navigation
• Search functionality helps find specific topics
• External links open relevant websites

For immediate assistance:
• Check Common Issues in Troubleshooting
• Review Getting Started for basic usage
• Explore Algorithm descriptions for technical details

The suite is designed for education and research - always use certified implementations for production systems.
"""
        
        self.content_display.insert(tk.END, overview_text)
    
    def show_contents(self):
        """Show table of contents"""
        self.content_header.config(text="Table of Contents")
        self.content_display.delete('1.0', tk.END)
        
        toc_text = """QUANTUM-SAFE CRYPTOGRAPHY SUITE - TABLE OF CONTENTS

1. OVERVIEW
   • Getting Started
   • Quick Tour
   • System Requirements

2. ALGORITHMS
   Classical Algorithms:
   • RSA - Rivest-Shamir-Adleman public key cryptosystem
   • ECDSA - Elliptic Curve Digital Signature Algorithm  
   • Ed25519 - Edwards curve signature scheme
   
   Post-Quantum Algorithms:
   • Dilithium - Lattice-based signatures (NIST standard)
   • Falcon - Compact lattice-based signatures (NIST standard)
   • SPHINCS+ - Hash-based signatures (NIST standard)  
   • Kyber - Lattice-based key encapsulation (NIST standard)

3. DEMONSTRATIONS
   • Hybrid TLS - TLS 1.3 key exchange comparison
   • Digital Signatures - Signature algorithm performance
   • Performance Benchmark - Comprehensive algorithm testing
   • QKD Simulation - Quantum key distribution with BB84
   • Migration Strategy - Enterprise migration planning

4. TROUBLESHOOTING
   • Common Issues - Import errors, GUI problems, memory usage
   • Performance Issues - Optimization tips and solutions

5. SECURITY
   • Algorithm Security - Quantum threats and resistance
   • Migration Considerations - Planning and strategy

6. REFERENCES  
   • NIST Standards - Official post-quantum standards
   • Academic Papers - Research publications
   • Online Resources - Websites and documentation

Navigate using the tree on the left or click topics to jump to specific sections.
"""
        
        self.content_display.insert(tk.END, toc_text)
    
    def search_help(self, event=None):
        """Search help content"""
        query = self.search_var.get().lower().strip()
        if not query:
            messagebox.showwarning("Search", "Please enter a search term.")
            return
        
        # Simple search implementation
        results = []
        
        def search_dict(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if query in key.lower():
                        results.append((current_path, f"Found in section: {key}"))
                    if isinstance(value, str) and query in value.lower():
                        results.append((current_path, f"Found in {key}: {value[:100]}..."))
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and query in item.lower():
                                results.append((current_path, f"Found in {key}: {item[:100]}..."))
                    elif isinstance(value, dict):
                        search_dict(value, current_path)
        
        search_dict(self.help_content)
        
        if results:
            self.show_search_results(query, results)
        else:
            messagebox.showinfo("Search Results", f"No results found for '{query}'.")
    
    def show_search_results(self, query: str, results: List):
        """Show search results"""
        self.content_header.config(text=f"Search Results for '{query}'")
        self.content_display.delete('1.0', tk.END)
        
        self.content_display.insert(tk.END, f"SEARCH RESULTS FOR: '{query}'\n")
        self.content_display.insert(tk.END, "=" * 40 + "\n\n")
        self.content_display.insert(tk.END, f"Found {len(results)} matches:\n\n")
        
        for i, (path, description) in enumerate(results, 1):
            self.content_display.insert(tk.END, f"{i}. {path}\n")
            self.content_display.insert(tk.END, f"   {description}\n\n")
        
        self.content_display.insert(tk.END, "\nTip: Use the navigation tree to view full content for any section.")
    
    def open_nist_pqc(self):
        """Open NIST Post-Quantum Cryptography website"""
        webbrowser.open("https://csrc.nist.gov/projects/post-quantum-cryptography")
    
    def open_oqs(self):
        """Open Open Quantum Safe website"""
        webbrowser.open("https://openquantumsafe.org/")

# Utility functions for help integration
def show_algorithm_help(algorithm_name: str, parent=None):
    """Show help for a specific algorithm"""
    help_system = HelpSystem(parent)
    help_system.show_help(f"algorithms.{algorithm_name}")

def show_demo_help(demo_name: str, parent=None):
    """Show help for a specific demonstration"""
    help_system = HelpSystem(parent)
    help_system.show_help(f"usage.{demo_name}")

def show_troubleshooting_help(parent=None):
    """Show troubleshooting help"""
    help_system = HelpSystem(parent)
    help_system.show_help("troubleshooting")

# Quick help dialogs for common questions
def show_quick_help(topic: str, parent=None):
    """Show quick help dialog for common topics"""
    quick_help_content = {
        "first_run": {
            "title": "First Time Running?",
            "content": """Welcome to the Quantum-Safe Cryptography Suite!

Quick Start Steps:
1. Start with the Dashboard tab
2. Click on a demonstration button to select it
3. Configure settings in the Configuration tab (optional)
4. Click 'Run Selected Demo' to start
5. View results in the Results tab

Recommended first demonstration:
• Digital Signatures - Shows algorithm comparison
• Quick benchmark mode for faster results

Need more help? Click Help → User Guide in the menu."""
        },
        "performance": {
            "title": "Performance Tips",
            "content": """Optimize Performance:

For Faster Execution:
• Use Quick mode (Configuration tab)
• Reduce benchmark iterations to 10-25
• Run individual demos instead of 'All'
• Close other applications

For Better Results:
• Ensure stable system load
• Use 100+ iterations for benchmarks
• Run on dedicated hardware when possible

Memory Requirements:
• Minimum: 4GB RAM
• Recommended: 8GB+ RAM
• Benchmark suite may use 1GB+ temporarily"""
        },
        "algorithms": {
            "title": "Algorithm Selection Guide",
            "content": """Choosing Algorithms:

For Current Use:
• RSA 2048+ for compatibility
• ECDSA for efficiency
• Ed25519 for performance

For Future Security:
• Dilithium for general use
• Falcon for size-constrained environments
• SPHINCS+ for ultra-conservative security

Migration Strategy:
• Start with hybrid approaches
• Plan for 5-10 year transition
• Consider performance requirements"""
        }
    }
    
    if topic in quick_help_content:
        info = quick_help_content[topic]
        messagebox.showinfo(info["title"], info["content"])
    else:
        messagebox.showinfo("Help", f"No quick help available for {topic}")

if __name__ == "__main__":
    # Test the help system
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    help_system = HelpSystem()
    help_system.show_help()
    
    root.mainloop()
