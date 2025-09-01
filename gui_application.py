#!/usr/bin/env python3
"""
Quantum-Safe Cryptography Suite - GUI Application
A modern graphical user interface for the quantum-safe cryptography demonstration suite

This GUI provides an intuitive interface to:
1. Run various cryptographic demonstrations
2. View and analyze results
3. Configure algorithm parameters
4. Access help and documentation
5. Export results and reports

Usage:
    python gui_application.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import webbrowser
from dataclasses import asdict

# Import the core suite modules
try:
    from main import QuantumSafeCryptoSuite
    from hybrid_tls import CryptoAlgorithm, KeyExchangeType
    from quantum_signatures import SignatureAlgorithm
    from performance_benchmark import CryptographicBenchmark
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import required modules: {e}")
    sys.exit(1)

class QuantumSafeGUI:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quantum-Safe Cryptography Suite v1.0.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize the crypto suite
        self.crypto_suite = QuantumSafeCryptoSuite()
        
        # GUI state
        self.current_demo = None
        self.demo_results = {}
        self.is_running_demo = False
        
        # Create GUI theme
        self.setup_theme()
        
        # Create the main interface
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_theme(self):
        """Configure the application theme and styling"""
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define color scheme
        self.colors = {
            'primary': '#2E3B4E',
            'secondary': '#3D5A80', 
            'accent': '#98C1D9',
            'success': '#52C41A',
            'warning': '#FA8C16',
            'error': '#FF4D4F',
            'background': '#F5F5F5',
            'surface': '#FFFFFF',
            'text_primary': '#262626',
            'text_secondary': '#8C8C8C'
        }
        
        # Configure styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=self.colors['primary'])
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'), foreground=self.colors['primary'])
        style.configure('Info.TLabel', font=('Segoe UI', 10), foreground=self.colors['text_secondary'])
        style.configure('Success.TLabel', font=('Segoe UI', 10), foreground=self.colors['success'])
        style.configure('Warning.TLabel', font=('Segoe UI', 10), foreground=self.colors['warning'])
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground=self.colors['error'])
        
        # Configure button styles
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Secondary.TButton', font=('Segoe UI', 10))
        
        # Configure notebook styles
        style.configure('TNotebook', background=self.colors['background'])
        style.configure('TNotebook.Tab', padding=(20, 10))
        
        # Configure progress bar
        style.configure('TProgressbar', background=self.colors['accent'])
    
    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_command(label="Import Settings...", command=self.import_settings)
        file_menu.add_command(label="Export Settings...", command=self.export_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Demonstrations menu
        demo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Demonstrations", menu=demo_menu)
        demo_menu.add_command(label="Hybrid TLS", command=lambda: self.run_demo('tls'))
        demo_menu.add_command(label="Digital Signatures", command=lambda: self.run_demo('signatures'))
        demo_menu.add_command(label="Client-Server Apps", command=lambda: self.run_demo('client_server'))
        demo_menu.add_command(label="Performance Benchmark", command=lambda: self.run_demo('benchmark'))
        demo_menu.add_command(label="QKD Simulation", command=lambda: self.run_demo('qkd'))
        demo_menu.add_command(label="Migration Strategy", command=lambda: self.run_demo('migration'))
        demo_menu.add_command(label="Extended Algorithms", command=lambda: self.run_demo('extended'))
        demo_menu.add_separator()
        demo_menu.add_command(label="Run All Demonstrations", command=lambda: self.run_demo('all'))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Algorithm Comparison", command=self.open_algorithm_comparison)
        tools_menu.add_command(label="Security Calculator", command=self.open_security_calculator)
        tools_menu.add_command(label="Performance Analyzer", command=self.open_performance_analyzer)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.open_user_guide)
        help_menu.add_command(label="Algorithm References", command=self.open_algorithm_references)
        help_menu.add_command(label="Troubleshooting", command=self.open_troubleshooting)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create the main application interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.create_dashboard_tab()
        
        # Results tab
        self.create_results_tab()
        
        # Configuration tab
        self.create_config_tab()
        
        # Logs tab
        self.create_logs_tab()
    
    def create_dashboard_tab(self):
        """Create the main dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")
        
        # Welcome section
        welcome_frame = ttk.LabelFrame(dashboard_frame, text="Welcome to Quantum-Safe Cryptography Suite")
        welcome_frame.pack(fill=tk.X, padx=10, pady=10)
        
        welcome_text = """
        This comprehensive suite demonstrates post-quantum cryptography algorithms and protocols.
        Select a demonstration below to explore different aspects of quantum-safe cryptography.
        """
        ttk.Label(welcome_frame, text=welcome_text, style='Info.TLabel', wraplength=800).pack(padx=20, pady=15)
        
        # Demonstrations grid
        demo_frame = ttk.LabelFrame(dashboard_frame, text="Demonstrations")
        demo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create demo buttons in a grid
        self.create_demo_buttons(demo_frame)
        
        # Progress section
        progress_frame = ttk.LabelFrame(dashboard_frame, text="Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_var = tk.StringVar(value="Ready to start demonstrations")
        ttk.Label(progress_frame, textvariable=self.progress_var, style='Info.TLabel').pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(progress_frame)
        control_frame.pack(pady=10)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Run Selected Demo", 
                                     command=self.run_selected_demo, style='Primary.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Stop", 
                                    command=self.stop_demo, style='Secondary.TButton', state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="📊 View Results", 
                  command=lambda: self.notebook.select(1), style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
    
    def create_demo_buttons(self, parent):
        """Create demonstration selection buttons"""
        demos = [
            ("🔐 Hybrid TLS", "tls", "Demonstrate hybrid TLS 1.3 handshakes\nwith classical and post-quantum algorithms"),
            ("✍️ Digital Signatures", "signatures", "Test quantum-safe digital signatures\nincluding Dilithium, Falcon, and SPHINCS+"),
            ("🌐 Client-Server Apps", "client_server", "Show crypto-agile networking\nwith automatic algorithm switching"),
            ("⚡ Performance Benchmark", "benchmark", "Comprehensive performance analysis\nof all supported algorithms"),
            ("🔬 QKD Simulation", "qkd", "BB84 quantum key distribution\nwith eavesdropping detection"),
            ("🛡️ Migration Strategy", "migration", "Enterprise migration planning\nand risk assessment tools"),
            ("🧪 Extended Algorithms", "extended", "Additional post-quantum algorithms\nincluding NTRU and McEliece"),
            ("🚀 All Demonstrations", "all", "Run complete demonstration suite\nwith all available tests")
        ]
        
        # Create buttons in a grid layout
        for i, (text, demo_id, description) in enumerate(demos):
            row = i // 2
            col = i % 2
            
            button_frame = ttk.Frame(parent)
            button_frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            # Configure grid weights
            parent.grid_columnconfigure(col, weight=1)
            
            btn = ttk.Button(button_frame, text=text, 
                           command=lambda d=demo_id: self.select_demo(d),
                           style='Secondary.TButton', width=20)
            btn.pack(anchor='w')
            
            ttk.Label(button_frame, text=description, style='Info.TLabel', 
                     wraplength=300).pack(anchor='w', pady=(5, 0))
        
        # Current selection
        self.selected_demo_var = tk.StringVar(value="No demonstration selected")
        selection_frame = ttk.Frame(parent)
        selection_frame.grid(row=len(demos)//2 + 1, column=0, columnspan=2, pady=20)
        
        ttk.Label(selection_frame, text="Selected:", style='Heading.TLabel').pack(side=tk.LEFT)
        ttk.Label(selection_frame, textvariable=self.selected_demo_var, 
                 style='Info.TLabel').pack(side=tk.LEFT, padx=10)
    
    def create_results_tab(self):
        """Create the results viewing tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Results")
        
        # Results selector
        selector_frame = ttk.Frame(results_frame)
        selector_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selector_frame, text="View Results:", style='Heading.TLabel').pack(side=tk.LEFT)
        
        self.results_combo = ttk.Combobox(selector_frame, state='readonly', width=30)
        self.results_combo.pack(side=tk.LEFT, padx=10)
        self.results_combo.bind('<<ComboboxSelected>>', self.on_results_selection)
        
        ttk.Button(selector_frame, text="📋 Export", 
                  command=self.export_current_results).pack(side=tk.RIGHT, padx=5)
        ttk.Button(selector_frame, text="🔄 Refresh", 
                  command=self.refresh_results).pack(side=tk.RIGHT, padx=5)
        
        # Results display area
        self.results_display = scrolledtext.ScrolledText(results_frame, 
                                                       font=('Consolas', 10),
                                                       wrap=tk.WORD)
        self.results_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial message
        self.results_display.insert(tk.END, "No results available yet.\nRun a demonstration to see results here.")
    
    def create_config_tab(self):
        """Create the configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuration")
        
        # Algorithm selection
        algo_frame = ttk.LabelFrame(config_frame, text="Algorithm Configuration")
        algo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # TLS algorithms
        tls_frame = ttk.Frame(algo_frame)
        tls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(tls_frame, text="Default TLS Algorithm:", style='Heading.TLabel').pack(anchor='w')
        self.tls_algo_var = tk.StringVar(value="X25519")
        tls_combo = ttk.Combobox(tls_frame, textvariable=self.tls_algo_var, 
                               values=[algo.value for algo in CryptoAlgorithm],
                               state='readonly')
        tls_combo.pack(anchor='w', pady=5)
        
        # Signature algorithms
        sig_frame = ttk.Frame(algo_frame)
        sig_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(sig_frame, text="Default Signature Algorithm:", style='Heading.TLabel').pack(anchor='w')
        self.sig_algo_var = tk.StringVar(value="DILITHIUM3")
        sig_combo = ttk.Combobox(sig_frame, textvariable=self.sig_algo_var,
                               values=[algo.value for algo in SignatureAlgorithm],
                               state='readonly')
        sig_combo.pack(anchor='w', pady=5)
        
        # Performance settings
        perf_frame = ttk.LabelFrame(config_frame, text="Performance Settings")
        perf_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Benchmark iterations
        iter_frame = ttk.Frame(perf_frame)
        iter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(iter_frame, text="Benchmark Iterations:", style='Heading.TLabel').pack(anchor='w')
        self.iterations_var = tk.IntVar(value=25)
        iter_scale = ttk.Scale(iter_frame, from_=10, to=200, variable=self.iterations_var, orient='horizontal')
        iter_scale.pack(fill=tk.X, pady=5)
        ttk.Label(iter_frame, text="Current: 25 iterations", style='Info.TLabel').pack(anchor='w')
        
        # Update label when scale changes
        def update_iter_label(*args):
            iter_scale.pack_info()['after'] = ttk.Label(iter_frame, 
                text=f"Current: {self.iterations_var.get()} iterations", 
                style='Info.TLabel').pack(anchor='w')
        
        self.iterations_var.trace('w', update_iter_label)
        
        # GUI preferences
        gui_frame = ttk.LabelFrame(config_frame, text="GUI Preferences")
        gui_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gui_frame, text="Auto-scroll results", 
                       variable=self.auto_scroll_var).pack(anchor='w', padx=10, pady=5)
        
        self.show_warnings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gui_frame, text="Show warning dialogs", 
                       variable=self.show_warnings_var).pack(anchor='w', padx=10, pady=5)
        
        self.verbose_output_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(gui_frame, text="Verbose output", 
                       variable=self.verbose_output_var).pack(anchor='w', padx=10, pady=5)
    
    def create_logs_tab(self):
        """Create the logs and console tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 Logs")
        
        # Log controls
        control_frame = ttk.Frame(logs_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="🗑️ Clear Logs", 
                  command=self.clear_logs).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="💾 Save Logs", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
        # Log level selector
        ttk.Label(control_frame, text="Log Level:").pack(side=tk.RIGHT, padx=5)
        self.log_level_var = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(control_frame, textvariable=self.log_level_var,
                               values=["DEBUG", "INFO", "WARNING", "ERROR"],
                               state='readonly', width=10)
        log_combo.pack(side=tk.RIGHT)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(logs_frame, 
                                                   font=('Consolas', 9),
                                                   wrap=tk.WORD)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add initial log entry
        self.log_message("INFO", "Application started successfully")
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(self.status_bar, textvariable=self.status_var, 
                               style='Info.TLabel')
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Version info
        version_label = ttk.Label(self.status_bar, text="v1.0.0", 
                                style='Info.TLabel')
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def select_demo(self, demo_id):
        """Select a demonstration to run"""
        demo_names = {
            'tls': 'Hybrid TLS Handshakes',
            'signatures': 'Digital Signatures', 
            'client_server': 'Client-Server Applications',
            'benchmark': 'Performance Benchmark',
            'qkd': 'QKD Simulation',
            'migration': 'Migration Strategy',
            'extended': 'Extended Algorithms',
            'all': 'All Demonstrations'
        }
        
        self.current_demo = demo_id
        self.selected_demo_var.set(demo_names.get(demo_id, f"Demo: {demo_id}"))
        self.start_button.config(state='normal')
        self.log_message("INFO", f"Selected demonstration: {demo_names.get(demo_id, demo_id)}")
    
    def run_selected_demo(self):
        """Run the currently selected demonstration"""
        if not self.current_demo:
            messagebox.showwarning("No Selection", "Please select a demonstration first.")
            return
        
        self.run_demo(self.current_demo)
    
    def run_demo(self, demo_id):
        """Run a specific demonstration in a separate thread"""
        if self.is_running_demo:
            messagebox.showwarning("Demo Running", "A demonstration is already running. Please wait for it to complete.")
            return
        
        # Update UI state
        self.is_running_demo = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start(10)
        
        # Run in separate thread to prevent GUI freezing
        demo_thread = threading.Thread(target=self._run_demo_thread, args=(demo_id,))
        demo_thread.daemon = True
        demo_thread.start()
    
    def _run_demo_thread(self, demo_id):
        """Run demonstration in a separate thread"""
        try:
            self.update_progress(f"Starting {demo_id} demonstration...")
            self.log_message("INFO", f"Starting {demo_id} demonstration")
            
            # Map demo IDs to suite methods
            demo_methods = {
                'tls': self.crypto_suite.demo_hybrid_tls,
                'signatures': self.crypto_suite.demo_quantum_signatures,
                'client_server': self.crypto_suite.demo_client_server,
                'benchmark': lambda: self.crypto_suite.demo_performance_benchmark(
                    quick_mode=(self.iterations_var.get() < 50)),
                'qkd': self.crypto_suite.demo_qkd_simulation,
                'migration': self.crypto_suite.demo_migration_strategy,
                'extended': self.crypto_suite.demo_extended_algorithms,
                'all': self.crypto_suite.run_all_demos
            }
            
            if demo_id in demo_methods:
                start_time = time.time()
                result = demo_methods[demo_id]()
                end_time = time.time()
                
                # Store results
                self.demo_results[demo_id] = {
                    'result': result,
                    'timestamp': datetime.now(),
                    'duration': end_time - start_time,
                    'demo_type': demo_id
                }
                
                self.update_progress(f"✅ {demo_id} demonstration completed successfully!")
                self.log_message("INFO", f"{demo_id} demonstration completed in {end_time - start_time:.2f}s")
                
                # Update results combo
                self.root.after(0, self.refresh_results_combo)
                
                # Show results
                if demo_id != 'all':
                    self.root.after(0, lambda: self.show_demo_results(demo_id))
            else:
                self.update_progress(f"❌ Unknown demonstration: {demo_id}")
                self.log_message("ERROR", f"Unknown demonstration: {demo_id}")
                
        except Exception as e:
            self.update_progress(f"❌ Error in {demo_id}: {str(e)}")
            self.log_message("ERROR", f"Error in {demo_id}: {str(e)}")
            messagebox.showerror("Demonstration Error", f"An error occurred during the {demo_id} demonstration:\n\n{str(e)}")
        
        finally:
            # Reset UI state
            self.root.after(0, self._demo_finished)
    
    def _demo_finished(self):
        """Called when a demonstration finishes"""
        self.is_running_demo = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
    
    def stop_demo(self):
        """Stop the current demonstration (placeholder - actual implementation would need thread coordination)"""
        messagebox.showinfo("Stop Demo", "Demo stopping is not yet implemented. The current demonstration will complete normally.")
        self.log_message("WARNING", "Demo stop requested (not implemented)")
    
    def update_progress(self, message):
        """Update the progress display"""
        def update():
            self.progress_var.set(message)
            self.status_var.set(message)
        
        self.root.after(0, update)
    
    def log_message(self, level, message):
        """Add a message to the log display"""
        def add_log():
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            self.log_display.insert(tk.END, log_entry)
            if self.auto_scroll_var.get():
                self.log_display.see(tk.END)
        
        self.root.after(0, add_log)
    
    def refresh_results_combo(self):
        """Refresh the results selection combo box"""
        demo_names = {
            'tls': 'Hybrid TLS Results',
            'signatures': 'Digital Signatures Results',
            'client_server': 'Client-Server Results', 
            'benchmark': 'Performance Benchmark Results',
            'qkd': 'QKD Simulation Results',
            'migration': 'Migration Strategy Results',
            'extended': 'Extended Algorithms Results',
            'all': 'All Demonstrations Results'
        }
        
        values = [demo_names.get(demo_id, f"{demo_id} Results") 
                 for demo_id in self.demo_results.keys()]
        self.results_combo['values'] = values
        
        if values and not self.results_combo.get():
            self.results_combo.set(values[-1])  # Select the most recent result
    
    def on_results_selection(self, event):
        """Handle results selection change"""
        selection = self.results_combo.get()
        # Find the corresponding demo_id
        demo_names = {
            'Hybrid TLS Results': 'tls',
            'Digital Signatures Results': 'signatures',
            'Client-Server Results': 'client_server',
            'Performance Benchmark Results': 'benchmark', 
            'QKD Simulation Results': 'qkd',
            'Migration Strategy Results': 'migration',
            'Extended Algorithms Results': 'extended',
            'All Demonstrations Results': 'all'
        }
        
        demo_id = demo_names.get(selection)
        if demo_id and demo_id in self.demo_results:
            self.show_demo_results(demo_id)
    
    def show_demo_results(self, demo_id):
        """Display results for a specific demonstration"""
        if demo_id not in self.demo_results:
            return
        
        result_data = self.demo_results[demo_id]
        
        # Clear current results
        self.results_display.delete('1.0', tk.END)
        
        # Format and display results
        output = []
        output.append(f"=== {demo_id.upper()} DEMONSTRATION RESULTS ===")
        output.append(f"Completed: {result_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Duration: {result_data['duration']:.2f} seconds")
        output.append("=" * 50)
        output.append("")
        
        # Format specific results based on demo type
        result = result_data['result']
        
        if demo_id == 'tls' and isinstance(result, list):
            output.append("TLS HANDSHAKE RESULTS:")
            output.append("-" * 30)
            for name, res, duration in result:
                output.append(f"Configuration: {name}")
                output.append(f"  Duration: {duration:.3f}s")
                output.append(f"  Algorithms: {', '.join(res['algorithms'])}")
                output.append(f"  Key Size: {res['shared_secret_size']} bytes")
                output.append(f"  Efficiency: {res['protocol_efficiency']*100:.1f}%")
                output.append("")
        
        elif demo_id == 'signatures' and isinstance(result, list):
            output.append("DIGITAL SIGNATURE RESULTS:")
            output.append("-" * 35)
            output.append(f"{'Algorithm':<20} {'Sign(ms)':<10} {'Verify(ms)':<12} {'Sig Size':<10}")
            output.append("-" * 55)
            for res in result:
                output.append(f"{res['algorithm']:<20} {res['sign_ms']:<10.2f} {res['verify_ms']:<12.2f} {res['signature_size']:<10}")
        
        elif demo_id == 'benchmark' and isinstance(result, dict):
            output.append("PERFORMANCE BENCHMARK RESULTS:")
            output.append("-" * 40)
            for category, results in result.items():
                if results:
                    output.append(f"\n{category.upper()} Results:")
                    for res in results[:5]:  # Show top 5
                        output.append(f"  {res.algorithm}: {res.mean:.2f}ms")
        
        else:
            # Generic result formatting
            output.append("DEMONSTRATION RESULTS:")
            output.append("-" * 25)
            output.append(str(result))
        
        # Insert results into display
        self.results_display.insert(tk.END, "\n".join(output))
        
        # Switch to results tab
        self.notebook.select(1)
    
    def refresh_results(self):
        """Refresh the current results display"""
        selection = self.results_combo.get()
        if selection:
            # Trigger selection event
            self.on_results_selection(None)
    
    def export_current_results(self):
        """Export the currently displayed results"""
        if not self.results_display.get('1.0', tk.END).strip():
            messagebox.showwarning("No Results", "No results to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Results"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.results_display.get('1.0', tk.END))
                messagebox.showinfo("Export Success", f"Results exported to {filename}")
                self.log_message("INFO", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
                self.log_message("ERROR", f"Export failed: {e}")
    
    def export_results(self):
        """Export all results to a file"""
        if not self.demo_results:
            messagebox.showwarning("No Results", "No demonstration results available to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export All Results"
        )
        
        if filename:
            try:
                export_data = {}
                for demo_id, data in self.demo_results.items():
                    export_data[demo_id] = {
                        'timestamp': data['timestamp'].isoformat(),
                        'duration': data['duration'],
                        'result': str(data['result'])  # Convert to string for JSON compatibility
                    }
                
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(export_data, f, indent=2)
                else:
                    with open(filename, 'w') as f:
                        for demo_id, data in export_data.items():
                            f.write(f"=== {demo_id.upper()} ===\n")
                            f.write(f"Timestamp: {data['timestamp']}\n")
                            f.write(f"Duration: {data['duration']:.2f}s\n")
                            f.write(f"Result: {data['result']}\n\n")
                
                messagebox.showinfo("Export Success", f"All results exported to {filename}")
                self.log_message("INFO", f"All results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
                self.log_message("ERROR", f"Export failed: {e}")
    
    def import_settings(self):
        """Import configuration settings from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Settings"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)
                
                # Apply settings
                if 'tls_algorithm' in settings:
                    self.tls_algo_var.set(settings['tls_algorithm'])
                if 'signature_algorithm' in settings:
                    self.sig_algo_var.set(settings['signature_algorithm'])
                if 'benchmark_iterations' in settings:
                    self.iterations_var.set(settings['benchmark_iterations'])
                if 'auto_scroll' in settings:
                    self.auto_scroll_var.set(settings['auto_scroll'])
                if 'show_warnings' in settings:
                    self.show_warnings_var.set(settings['show_warnings'])
                if 'verbose_output' in settings:
                    self.verbose_output_var.set(settings['verbose_output'])
                
                messagebox.showinfo("Import Success", "Settings imported successfully.")
                self.log_message("INFO", f"Settings imported from {filename}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import settings:\n{e}")
                self.log_message("ERROR", f"Settings import failed: {e}")
    
    def export_settings(self):
        """Export current configuration settings to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Settings"
        )
        
        if filename:
            try:
                settings = {
                    'tls_algorithm': self.tls_algo_var.get(),
                    'signature_algorithm': self.sig_algo_var.get(),
                    'benchmark_iterations': self.iterations_var.get(),
                    'auto_scroll': self.auto_scroll_var.get(),
                    'show_warnings': self.show_warnings_var.get(),
                    'verbose_output': self.verbose_output_var.get(),
                    'export_timestamp': datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                messagebox.showinfo("Export Success", f"Settings exported to {filename}")
                self.log_message("INFO", f"Settings exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export settings:\n{e}")
                self.log_message("ERROR", f"Settings export failed: {e}")
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.delete('1.0', tk.END)
        self.log_message("INFO", "Logs cleared")
    
    def save_logs(self):
        """Save logs to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Logs"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_display.get('1.0', tk.END))
                messagebox.showinfo("Save Success", f"Logs saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save logs:\n{e}")
    
    def open_algorithm_comparison(self):
        """Open algorithm comparison tool (placeholder)"""
        messagebox.showinfo("Algorithm Comparison", "Algorithm comparison tool coming soon!")
    
    def open_security_calculator(self):
        """Open security calculator tool (placeholder)"""
        messagebox.showinfo("Security Calculator", "Security calculator tool coming soon!")
    
    def open_performance_analyzer(self):
        """Open performance analyzer tool (placeholder)"""
        messagebox.showinfo("Performance Analyzer", "Performance analyzer tool coming soon!")
    
    def open_settings(self):
        """Open advanced settings dialog (placeholder)"""
        messagebox.showinfo("Settings", "Advanced settings dialog coming soon!")
    
    def open_user_guide(self):
        """Open user guide"""
        messagebox.showinfo("User Guide", "User guide will be displayed in the default web browser.")
        # In a real implementation, you might open a local HTML file or URL
    
    def open_algorithm_references(self):
        """Open algorithm references"""
        messagebox.showinfo("Algorithm References", "Algorithm references coming soon!")
    
    def open_troubleshooting(self):
        """Open troubleshooting guide"""
        messagebox.showinfo("Troubleshooting", "Troubleshooting guide coming soon!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""Quantum-Safe Cryptography Suite v1.0.0

A comprehensive demonstration and analysis platform for post-quantum cryptography.

Features:
• Hybrid TLS 1.3 Handshakes
• Digital Signatures (Dilithium, Falcon, SPHINCS+)
• Client-Server Applications with Crypto-Agility
• Performance Benchmarking
• BB84 Quantum Key Distribution Simulation
• Migration Strategy & Threat Analysis
• Extended Algorithm Support

Built with Python and Tkinter
© 2024 Quantum-Safe Cryptography Suite

For educational and research purposes only.
"""
        
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_running_demo:
            if messagebox.askokcancel("Quit", "A demonstration is running. Do you want to quit anyway?"):
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main entry point for the GUI application"""
    try:
        app = QuantumSafeGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start the application:\n\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
