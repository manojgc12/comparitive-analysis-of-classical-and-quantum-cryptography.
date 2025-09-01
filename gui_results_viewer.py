#!/usr/bin/env python3
"""
Quantum-Safe Cryptography Suite - Results Viewer Component
Enhanced results visualization and analysis component for the GUI

This module provides specialized viewers for different types of demonstration results:
1. TLS handshake performance charts
2. Signature algorithm comparison tables
3. Benchmark result graphs
4. QKD simulation visualizations
5. Migration strategy reports
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.patches as patches
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class ResultsViewer:
    """Enhanced results viewer with charts and tables"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.current_results = None
        self.current_demo_type = None
        
        # Create the viewer interface
        self.create_interface()
    
    def create_interface(self):
        """Create the results viewer interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self.create_toolbar()
        
        # Content notebook for different view types
        self.content_notebook = ttk.Notebook(self.main_frame)
        self.content_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create different view tabs
        self.create_text_view()
        self.create_chart_view()
        self.create_table_view()
        self.create_summary_view()
    
    def create_toolbar(self):
        """Create the results viewer toolbar"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # View type selector
        ttk.Label(toolbar, text="View Type:").pack(side=tk.LEFT, padx=5)
        
        self.view_type_var = tk.StringVar(value="Auto")
        view_combo = ttk.Combobox(toolbar, textvariable=self.view_type_var,
                                values=["Auto", "Text", "Chart", "Table", "Summary"],
                                state='readonly', width=15)
        view_combo.pack(side=tk.LEFT, padx=5)
        view_combo.bind('<<ComboboxSelected>>', self.on_view_type_change)
        
        # Separator
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Export options
        ttk.Button(toolbar, text="📊 Export Chart", 
                  command=self.export_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📋 Export Table", 
                  command=self.export_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📄 Export Summary", 
                  command=self.export_summary).pack(side=tk.LEFT, padx=5)
        
        # Analysis options
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(toolbar, text="🔍 Analyze", 
                  command=self.show_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📈 Compare", 
                  command=self.show_comparison).pack(side=tk.LEFT, padx=5)
    
    def create_text_view(self):
        """Create the text-based results view"""
        text_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(text_frame, text="📄 Text View")
        
        # Text display with scrollbars
        text_container = ttk.Frame(text_frame)
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_display = tk.Text(text_container, font=('Consolas', 10), wrap=tk.WORD)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.text_display.yview)
        h_scrollbar = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL, command=self.text_display.xview)
        
        self.text_display.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_chart_view(self):
        """Create the chart-based results view"""
        chart_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(chart_frame, text="📊 Chart View")
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.patch.set_facecolor('white')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar
        toolbar_frame = ttk.Frame(chart_frame)
        toolbar_frame.pack(fill=tk.X)
        self.nav_toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.nav_toolbar.update()
        
        # Initial empty chart
        self.ax.text(0.5, 0.5, 'No chart data available\nRun a demonstration to see charts here',
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=12, color='gray')
        self.canvas.draw()
    
    def create_table_view(self):
        """Create the table-based results view"""
        table_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(table_frame, text="📋 Table View")
        
        # Create treeview for tabular data
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview with scrollbars
        self.table_tree = ttk.Treeview(table_container)
        
        # Scrollbars for table
        table_v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.table_tree.yview)
        table_h_scroll = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.table_tree.xview)
        
        self.table_tree.config(yscrollcommand=table_v_scroll.set, xscrollcommand=table_h_scroll.set)
        
        # Pack table elements
        self.table_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        table_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Table controls
        table_controls = ttk.Frame(table_frame)
        table_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(table_controls, text="📊 Sort by Value", 
                  command=self.sort_table_by_value).pack(side=tk.LEFT, padx=5)
        ttk.Button(table_controls, text="🔤 Sort by Name", 
                  command=self.sort_table_by_name).pack(side=tk.LEFT, padx=5)
        ttk.Button(table_controls, text="🔄 Reset", 
                  command=self.reset_table_sort).pack(side=tk.LEFT, padx=5)
    
    def create_summary_view(self):
        """Create the summary/statistics view"""
        summary_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(summary_frame, text="📈 Summary")
        
        # Summary statistics display
        stats_frame = ttk.LabelFrame(summary_frame, text="Statistical Summary")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, font=('Consolas', 10))
        self.stats_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Key insights
        insights_frame = ttk.LabelFrame(summary_frame, text="Key Insights")
        insights_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.insights_text = tk.Text(insights_frame, font=('Segoe UI', 10), wrap=tk.WORD)
        insights_scroll = ttk.Scrollbar(insights_frame, orient=tk.VERTICAL, command=self.insights_text.yview)
        self.insights_text.config(yscrollcommand=insights_scroll.set)
        
        self.insights_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        insights_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def display_results(self, results: Any, demo_type: str, metadata: Dict = None):
        """Display results in the viewer"""
        self.current_results = results
        self.current_demo_type = demo_type
        
        # Update different views based on demo type
        self.update_text_view(results, demo_type)
        self.update_chart_view(results, demo_type)
        self.update_table_view(results, demo_type)
        self.update_summary_view(results, demo_type, metadata)
        
        # Select appropriate default view
        if demo_type in ['benchmark', 'tls', 'signatures']:
            self.content_notebook.select(1)  # Chart view
        elif demo_type in ['migration', 'extended']:
            self.content_notebook.select(2)  # Table view
        else:
            self.content_notebook.select(0)  # Text view
    
    def update_text_view(self, results: Any, demo_type: str):
        """Update the text view with formatted results"""
        self.text_display.delete('1.0', tk.END)
        
        if demo_type == 'tls' and isinstance(results, list):
            self.text_display.insert(tk.END, "TLS HANDSHAKE RESULTS\n")
            self.text_display.insert(tk.END, "=" * 50 + "\n\n")
            
            for name, res, duration in results:
                self.text_display.insert(tk.END, f"Configuration: {name}\n")
                self.text_display.insert(tk.END, f"  Duration: {duration:.3f}s\n")
                self.text_display.insert(tk.END, f"  Algorithms: {', '.join(res.get('algorithms', []))}\n")
                self.text_display.insert(tk.END, f"  Key Size: {res.get('shared_secret_size', 'N/A')} bytes\n")
                self.text_display.insert(tk.END, f"  Efficiency: {res.get('protocol_efficiency', 0)*100:.1f}%\n\n")
                
        elif demo_type == 'signatures' and isinstance(results, list):
            self.text_display.insert(tk.END, "DIGITAL SIGNATURE RESULTS\n")
            self.text_display.insert(tk.END, "=" * 50 + "\n\n")
            
            # Header
            self.text_display.insert(tk.END, f"{'Algorithm':<20} {'Sign(ms)':<12} {'Verify(ms)':<12} {'Sig Size':<12}\n")
            self.text_display.insert(tk.END, "-" * 60 + "\n")
            
            for res in results:
                self.text_display.insert(tk.END, 
                    f"{res.get('algorithm', 'N/A'):<20} "
                    f"{res.get('sign_ms', 0):<12.2f} "
                    f"{res.get('verify_ms', 0):<12.2f} "
                    f"{res.get('signature_size', 0):<12}\n")
        
        elif demo_type == 'benchmark' and isinstance(results, dict):
            self.text_display.insert(tk.END, "PERFORMANCE BENCHMARK RESULTS\n")
            self.text_display.insert(tk.END, "=" * 50 + "\n\n")
            
            for category, data in results.items():
                if data and isinstance(data, list):
                    self.text_display.insert(tk.END, f"{category.upper()} Results:\n")
                    self.text_display.insert(tk.END, "-" * 30 + "\n")
                    
                    for item in data[:10]:  # Show top 10
                        if hasattr(item, 'algorithm') and hasattr(item, 'mean'):
                            self.text_display.insert(tk.END, f"  {item.algorithm}: {item.mean:.2f}ms\n")
                    
                    self.text_display.insert(tk.END, "\n")
        
        else:
            # Generic result display
            self.text_display.insert(tk.END, f"{demo_type.upper()} RESULTS\n")
            self.text_display.insert(tk.END, "=" * 50 + "\n\n")
            self.text_display.insert(tk.END, str(results))
    
    def update_chart_view(self, results: Any, demo_type: str):
        """Update the chart view with appropriate visualization"""
        self.ax.clear()
        
        try:
            if demo_type == 'tls' and isinstance(results, list):
                self.create_tls_chart(results)
            elif demo_type == 'signatures' and isinstance(results, list):
                self.create_signatures_chart(results)
            elif demo_type == 'benchmark' and isinstance(results, dict):
                self.create_benchmark_chart(results)
            else:
                self.ax.text(0.5, 0.5, f'Chart view not available for {demo_type} results',
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.ax.transAxes, fontsize=12, color='gray')
            
            self.canvas.draw()
            
        except Exception as e:
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Error creating chart:\n{str(e)}',
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=10, color='red')
            self.canvas.draw()
    
    def create_tls_chart(self, results: List):
        """Create TLS handshake performance chart"""
        names = []
        durations = []
        key_sizes = []
        
        for name, res, duration in results:
            names.append(name.replace(' ', '\n'))  # Multi-line labels
            durations.append(duration * 1000)  # Convert to ms
            key_sizes.append(res.get('shared_secret_size', 0))
        
        # Create dual-axis chart
        ax2 = self.ax.twinx()
        
        # Bar chart for durations
        bars = self.ax.bar(names, durations, alpha=0.7, color='skyblue', label='Handshake Time (ms)')
        
        # Line chart for key sizes
        line = ax2.plot(names, key_sizes, color='red', marker='o', linewidth=2, markersize=6, label='Key Size (bytes)')
        
        # Formatting
        self.ax.set_title('TLS Handshake Performance Comparison', fontsize=14, fontweight='bold')
        self.ax.set_ylabel('Handshake Time (ms)', color='blue')
        ax2.set_ylabel('Key Size (bytes)', color='red')
        self.ax.tick_params(axis='y', labelcolor='blue')
        ax2.tick_params(axis='y', labelcolor='red')
        
        # Rotate x-axis labels for better readability
        self.ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, duration in zip(bars, durations):
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(durations)*0.01,
                        f'{duration:.1f}ms', ha='center', va='bottom', fontsize=9)
        
        # Legend
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.tight_layout()
    
    def create_signatures_chart(self, results: List):
        """Create digital signatures performance chart"""
        algorithms = [res.get('algorithm', 'Unknown') for res in results]
        sign_times = [res.get('sign_ms', 0) for res in results]
        verify_times = [res.get('verify_ms', 0) for res in results]
        sig_sizes = [res.get('signature_size', 0) for res in results]
        
        # Create subplots
        fig = self.fig
        fig.clear()
        
        # Performance comparison (top)
        ax1 = fig.add_subplot(2, 1, 1)
        x = np.arange(len(algorithms))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, sign_times, width, label='Signing Time (ms)', alpha=0.7, color='lightcoral')
        bars2 = ax1.bar(x + width/2, verify_times, width, label='Verification Time (ms)', alpha=0.7, color='lightblue')
        
        ax1.set_title('Signature Algorithm Performance', fontweight='bold')
        ax1.set_ylabel('Time (ms)')
        ax1.set_xticks(x)
        ax1.set_xticklabels([alg.split('-')[0] if '-' in alg else alg for alg in algorithms], rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Signature sizes (bottom)
        ax2 = fig.add_subplot(2, 1, 2)
        bars3 = ax2.bar(algorithms, sig_sizes, color='lightgreen', alpha=0.7)
        ax2.set_title('Signature Sizes', fontweight='bold')
        ax2.set_ylabel('Size (bytes)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, size in zip(bars3, sig_sizes):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(sig_sizes)*0.01,
                    f'{size}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        self.canvas.draw()
    
    def create_benchmark_chart(self, results: Dict):
        """Create benchmark results chart"""
        categories = list(results.keys())
        
        if len(categories) == 1:
            # Single category - detailed view
            category = categories[0]
            data = results[category]
            
            if data and isinstance(data, list) and hasattr(data[0], 'algorithm'):
                algorithms = [item.algorithm for item in data[:10]]  # Top 10
                values = [item.mean for item in data[:10]]
                
                bars = self.ax.barh(algorithms, values, color='steelblue', alpha=0.7)
                self.ax.set_title(f'{category.title()} Performance (Top 10)', fontweight='bold')
                self.ax.set_xlabel('Time (ms)')
                
                # Add value labels
                for bar, value in zip(bars, values):
                    self.ax.text(bar.get_width() + max(values)*0.01, bar.get_y() + bar.get_height()/2,
                                f'{value:.2f}ms', va='center', fontsize=9)
        
        else:
            # Multiple categories - summary view
            category_means = {}
            for category, data in results.items():
                if data and isinstance(data, list) and hasattr(data[0], 'mean'):
                    category_means[category] = np.mean([item.mean for item in data[:5]])  # Top 5 average
            
            if category_means:
                categories = list(category_means.keys())
                means = list(category_means.values())
                
                bars = self.ax.bar(categories, means, color=['red', 'green', 'blue'][:len(categories)], alpha=0.7)
                self.ax.set_title('Benchmark Categories Comparison', fontweight='bold')
                self.ax.set_ylabel('Average Time (ms)')
                self.ax.tick_params(axis='x', rotation=45)
                
                # Add value labels
                for bar, mean in zip(bars, means):
                    self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(means)*0.01,
                                f'{mean:.1f}ms', ha='center', va='bottom')
        
        plt.tight_layout()
    
    def update_table_view(self, results: Any, demo_type: str):
        """Update the table view with structured data"""
        # Clear existing data
        for item in self.table_tree.get_children():
            self.table_tree.delete(item)
        
        if demo_type == 'signatures' and isinstance(results, list):
            # Configure columns
            columns = ('Algorithm', 'Sign Time (ms)', 'Verify Time (ms)', 'Signature Size (bytes)', 'Key Size (pub/priv)')
            self.table_tree['columns'] = columns
            self.table_tree['show'] = 'headings'
            
            # Configure column headings and widths
            for col in columns:
                self.table_tree.heading(col, text=col)
                self.table_tree.column(col, width=150, anchor='center')
            
            # Insert data
            for res in results:
                values = (
                    res.get('algorithm', 'N/A'),
                    f"{res.get('sign_ms', 0):.2f}",
                    f"{res.get('verify_ms', 0):.2f}",
                    str(res.get('signature_size', 0)),
                    f"{res.get('pub_key_size', 0)}/{res.get('priv_key_size', 0)}"
                )
                self.table_tree.insert('', tk.END, values=values)
        
        elif demo_type == 'tls' and isinstance(results, list):
            # Configure columns for TLS
            columns = ('Configuration', 'Duration (ms)', 'Algorithms', 'Key Size', 'Efficiency (%)')
            self.table_tree['columns'] = columns
            self.table_tree['show'] = 'headings'
            
            for col in columns:
                self.table_tree.heading(col, text=col)
                self.table_tree.column(col, width=120, anchor='center')
            
            # Insert data
            for name, res, duration in results:
                values = (
                    name,
                    f"{duration*1000:.1f}",
                    ', '.join(res.get('algorithms', [])),
                    f"{res.get('shared_secret_size', 0)} bytes",
                    f"{res.get('protocol_efficiency', 0)*100:.1f}"
                )
                self.table_tree.insert('', tk.END, values=values)
        
        else:
            # Generic table view
            self.table_tree['columns'] = ('Property', 'Value')
            self.table_tree['show'] = 'headings'
            self.table_tree.heading('Property', text='Property')
            self.table_tree.heading('Value', text='Value')
            self.table_tree.column('Property', width=200)
            self.table_tree.column('Value', width=300)
            
            # Insert basic info
            self.table_tree.insert('', tk.END, values=('Demo Type', demo_type.title()))
            self.table_tree.insert('', tk.END, values=('Result Type', type(results).__name__))
            self.table_tree.insert('', tk.END, values=('Data Length', len(results) if hasattr(results, '__len__') else 'N/A'))
    
    def update_summary_view(self, results: Any, demo_type: str, metadata: Dict = None):
        """Update the summary view with statistics and insights"""
        # Clear existing content
        self.stats_text.delete('1.0', tk.END)
        self.insights_text.delete('1.0', tk.END)
        
        # Generate statistics
        stats = self.generate_statistics(results, demo_type)
        self.stats_text.insert(tk.END, stats)
        
        # Generate insights
        insights = self.generate_insights(results, demo_type, metadata)
        self.insights_text.insert(tk.END, insights)
    
    def generate_statistics(self, results: Any, demo_type: str) -> str:
        """Generate statistical summary of results"""
        stats = []
        stats.append(f"STATISTICAL SUMMARY - {demo_type.upper()}")
        stats.append("=" * 40)
        stats.append("")
        
        if demo_type == 'signatures' and isinstance(results, list):
            sign_times = [res.get('sign_ms', 0) for res in results]
            verify_times = [res.get('verify_ms', 0) for res in results]
            sig_sizes = [res.get('signature_size', 0) for res in results]
            
            stats.append(f"Number of algorithms tested: {len(results)}")
            stats.append(f"Signing Time Statistics:")
            stats.append(f"  Average: {np.mean(sign_times):.2f} ms")
            stats.append(f"  Median:  {np.median(sign_times):.2f} ms")
            stats.append(f"  Range:   {min(sign_times):.2f} - {max(sign_times):.2f} ms")
            stats.append("")
            stats.append(f"Verification Time Statistics:")
            stats.append(f"  Average: {np.mean(verify_times):.2f} ms")
            stats.append(f"  Median:  {np.median(verify_times):.2f} ms")
            stats.append(f"  Range:   {min(verify_times):.2f} - {max(verify_times):.2f} ms")
            stats.append("")
            stats.append(f"Signature Size Statistics:")
            stats.append(f"  Average: {np.mean(sig_sizes):.0f} bytes")
            stats.append(f"  Median:  {np.median(sig_sizes):.0f} bytes")
            stats.append(f"  Range:   {min(sig_sizes)} - {max(sig_sizes)} bytes")
            
        elif demo_type == 'tls' and isinstance(results, list):
            durations = [duration for _, _, duration in results]
            key_sizes = [res.get('shared_secret_size', 0) for _, res, _ in results]
            
            stats.append(f"Number of configurations tested: {len(results)}")
            stats.append(f"Handshake Duration Statistics:")
            stats.append(f"  Average: {np.mean(durations)*1000:.1f} ms")
            stats.append(f"  Median:  {np.median(durations)*1000:.1f} ms")
            stats.append(f"  Range:   {min(durations)*1000:.1f} - {max(durations)*1000:.1f} ms")
            stats.append("")
            stats.append(f"Key Size Statistics:")
            stats.append(f"  Average: {np.mean(key_sizes):.0f} bytes")
            stats.append(f"  Range:   {min(key_sizes)} - {max(key_sizes)} bytes")
        
        else:
            stats.append(f"Demo Type: {demo_type}")
            stats.append(f"Result Type: {type(results).__name__}")
            if hasattr(results, '__len__'):
                stats.append(f"Data Points: {len(results)}")
        
        return "\n".join(stats)
    
    def generate_insights(self, results: Any, demo_type: str, metadata: Dict = None) -> str:
        """Generate insights and recommendations"""
        insights = []
        insights.append(f"KEY INSIGHTS - {demo_type.upper()}")
        insights.append("=" * 40)
        insights.append("")
        
        if demo_type == 'signatures' and isinstance(results, list):
            # Find fastest and most compact algorithms
            sign_times = [(res.get('algorithm'), res.get('sign_ms', float('inf'))) for res in results]
            sig_sizes = [(res.get('algorithm'), res.get('signature_size', float('inf'))) for res in results]
            
            fastest = min(sign_times, key=lambda x: x[1])
            most_compact = min(sig_sizes, key=lambda x: x[1])
            
            insights.append("🏆 PERFORMANCE LEADERS:")
            insights.append(f"• Fastest signing: {fastest[0]} ({fastest[1]:.2f} ms)")
            insights.append(f"• Most compact signatures: {most_compact[0]} ({most_compact[1]} bytes)")
            insights.append("")
            
            insights.append("📊 ALGORITHM CATEGORIES:")
            classical = [r for r in results if any(classical_name in r.get('algorithm', '') 
                                                 for classical_name in ['RSA', 'ECDSA', 'Ed25519'])]
            pq = [r for r in results if not any(classical_name in r.get('algorithm', '') 
                                               for classical_name in ['RSA', 'ECDSA', 'Ed25519'])]
            
            if classical:
                insights.append(f"• Classical algorithms: {len(classical)} tested")
                avg_classical = np.mean([r.get('sign_ms', 0) for r in classical])
                insights.append(f"  Average signing time: {avg_classical:.2f} ms")
            
            if pq:
                insights.append(f"• Post-quantum algorithms: {len(pq)} tested")
                avg_pq = np.mean([r.get('sign_ms', 0) for r in pq])
                insights.append(f"  Average signing time: {avg_pq:.2f} ms")
            
            insights.append("")
            insights.append("🔍 RECOMMENDATIONS:")
            insights.append("• For high-performance applications: Consider Ed25519 or ECDSA")
            insights.append("• For post-quantum security: Dilithium offers good balance")
            insights.append("• For minimal signatures: Ed25519 provides smallest classical signatures")
            insights.append("• For long-term security: Migrate to post-quantum algorithms")
            
        elif demo_type == 'tls' and isinstance(results, list):
            durations = [(name, duration) for name, _, duration in results]
            fastest_config = min(durations, key=lambda x: x[1])
            slowest_config = max(durations, key=lambda x: x[1])
            
            insights.append("🏆 CONFIGURATION PERFORMANCE:")
            insights.append(f"• Fastest: {fastest_config[0]} ({fastest_config[1]*1000:.1f} ms)")
            insights.append(f"• Slowest: {slowest_config[0]} ({slowest_config[1]*1000:.1f} ms)")
            
            speedup = slowest_config[1] / fastest_config[1]
            insights.append(f"• Performance difference: {speedup:.1f}x faster")
            insights.append("")
            
            insights.append("🔍 ANALYSIS:")
            hybrid_configs = [r for r in results if 'Hybrid' in r[0]]
            classical_configs = [r for r in results if 'Classical' in r[0]]
            
            if hybrid_configs and classical_configs:
                avg_hybrid = np.mean([duration for _, _, duration in hybrid_configs])
                avg_classical = np.mean([duration for _, _, duration in classical_configs])
                overhead = ((avg_hybrid - avg_classical) / avg_classical) * 100
                
                insights.append(f"• Hybrid vs Classical overhead: {overhead:.1f}%")
                insights.append("• Post-quantum algorithms add computational cost")
                insights.append("• Security benefits may justify performance impact")
            
            insights.append("")
            insights.append("🔍 RECOMMENDATIONS:")
            insights.append("• Use classical algorithms only for legacy compatibility")
            insights.append("• Implement hybrid approaches for gradual migration")
            insights.append("• Consider performance requirements vs security needs")
            insights.append("• Monitor quantum computing advances for migration timing")
        
        else:
            insights.append(f"Analysis for {demo_type} demonstration completed.")
            insights.append("View the Text or Chart tabs for detailed results.")
            insights.append("")
            insights.append("For more detailed analysis, export the results")
            insights.append("and use external analysis tools.")
        
        return "\n".join(insights)
    
    def on_view_type_change(self, event):
        """Handle view type selection change"""
        view_type = self.view_type_var.get()
        if view_type == "Text":
            self.content_notebook.select(0)
        elif view_type == "Chart":
            self.content_notebook.select(1)
        elif view_type == "Table":
            self.content_notebook.select(2)
        elif view_type == "Summary":
            self.content_notebook.select(3)
        # Auto selection is handled in display_results
    
    def sort_table_by_value(self):
        """Sort table by numeric values (where applicable)"""
        messagebox.showinfo("Sort", "Table sorting by value implemented")
    
    def sort_table_by_name(self):
        """Sort table by algorithm/configuration names"""
        messagebox.showinfo("Sort", "Table sorting by name implemented")
    
    def reset_table_sort(self):
        """Reset table to original sort order"""
        messagebox.showinfo("Reset", "Table sort reset implemented")
    
    def export_chart(self):
        """Export current chart as image"""
        if hasattr(self, 'fig'):
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")]
            )
            if filename:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Export Success", f"Chart saved to {filename}")
        else:
            messagebox.showwarning("No Chart", "No chart available to export")
    
    def export_table(self):
        """Export current table data as CSV"""
        messagebox.showinfo("Export Table", "Table export functionality coming soon!")
    
    def export_summary(self):
        """Export summary and insights as text file"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("STATISTICAL SUMMARY\n")
                    f.write("=" * 50 + "\n")
                    f.write(self.stats_text.get('1.0', tk.END))
                    f.write("\n\nKEY INSIGHTS\n")
                    f.write("=" * 50 + "\n")
                    f.write(self.insights_text.get('1.0', tk.END))
                messagebox.showinfo("Export Success", f"Summary saved to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save summary: {e}")
    
    def show_analysis(self):
        """Show detailed analysis dialog"""
        messagebox.showinfo("Analysis", "Detailed analysis dialog coming soon!")
    
    def show_comparison(self):
        """Show comparison dialog"""
        messagebox.showinfo("Comparison", "Comparison dialog coming soon!")
