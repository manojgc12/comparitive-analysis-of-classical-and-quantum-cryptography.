#!/usr/bin/env python3
"""
Quantum-Safe Cryptography Suite - GUI Launcher
Simple launcher script for the GUI application

Usage:
    python run_gui.py
    
Or double-click this file if Python is properly configured.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required modules are available"""
    required_modules = [
        'tkinter',
        'threading',
        'json',
        'datetime'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install the missing modules and try again.")
        return False
    
    return True

def check_crypto_modules():
    """Check if the crypto suite modules are available"""
    crypto_modules = [
        'main',
        'hybrid_tls',
        'quantum_signatures',
        'performance_benchmark'
    ]
    
    missing_modules = []
    
    for module in crypto_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"⚠️ Missing crypto modules: {', '.join(missing_modules)}")
        print("Some demonstrations may not work properly.")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🔐 Quantum-Safe Cryptography Suite - GUI Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    gui_file = current_dir / "gui_application.py"
    
    if not gui_file.exists():
        print("❌ GUI application not found!")
        print(f"Expected: {gui_file}")
        print("Please make sure you're running this from the quantum_safe_crypto directory.")
        return 1
    
    # Check requirements
    print("🔍 Checking requirements...")
    
    if not check_requirements():
        print("\n❌ Requirements check failed!")
        return 1
    
    print("✅ Basic requirements satisfied")
    
    # Check crypto modules (warning only)
    if not check_crypto_modules():
        print("⚠️ Some crypto modules missing, but continuing...")
    else:
        print("✅ All crypto modules found")
    
    print("\n🚀 Starting GUI application...")
    print("-" * 30)
    
    try:
        # Try to run the GUI application
        import gui_application
        gui_application.main()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI application: {e}")
        print("\nTrying to run as subprocess...")
        
        try:
            # Fallback: run as subprocess
            result = subprocess.run([sys.executable, "gui_application.py"], 
                                  check=True, capture_output=False)
            return result.returncode
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start GUI: {e}")
            return 1
        except FileNotFoundError:
            print("❌ Python interpreter not found!")
            return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code != 0:
        print(f"\n❌ Application exited with code {exit_code}")
        print("\nTroubleshooting:")
        print("1. Make sure all required Python packages are installed")
        print("2. Verify you're in the correct directory")
        print("3. Check that all crypto suite files are present")
        print("4. Try running: python gui_application.py directly")
        
        # Keep window open on Windows
        if os.name == 'nt':
            input("\nPress Enter to exit...")
    
    sys.exit(exit_code)
