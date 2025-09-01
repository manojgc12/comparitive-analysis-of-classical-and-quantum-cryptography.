"""
Quantum-Safe Cryptography Web Dashboard
A Flask web application providing a modern GUI for quantum-safe cryptographic operations
"""

import os
import json
import base64
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from werkzeug.utils import secure_filename
import logging
from quantum_signatures import (
    HybridSignatureSystem, 
    SignatureAlgorithm, 
    ClassicalSignature, 
    QuantumSafeSignature
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the quantum-safe signature system
sig_system = HybridSignatureSystem()

# Global storage for demo purposes (in production, use a database)
app_data = {
    'keypairs': {},
    'signatures': {},
    'certificates': {},
    'benchmark_results': None
}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', 
                         algorithms=SignatureAlgorithm, 
                         stats=get_dashboard_stats())

@app.route('/api/algorithms')
def get_algorithms():
    """Get list of supported algorithms"""
    algorithms = []
    for alg in SignatureAlgorithm:
        algorithms.append({
            'name': alg.name,
            'value': alg.value,
            'type': 'Post-Quantum' if alg.value.startswith(('Dilithium', 'Falcon', 'SPHINCS')) else 'Classical'
        })
    return jsonify(algorithms)

@app.route('/api/generate-keypair', methods=['POST'])
def generate_keypair():
    """Generate a new key pair for specified algorithm"""
    try:
        data = request.get_json()
        algorithm_name = data.get('algorithm')
        
        # Find the algorithm enum
        algorithm = None
        for alg in SignatureAlgorithm:
            if alg.value == algorithm_name:
                algorithm = alg
                break
        
        if not algorithm:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
        # Generate keypair
        keypair = sig_system.create_keypair(algorithm)
        
        # Store keypair (encode bytes as base64 for JSON)
        keypair_id = secrets.token_hex(8)
        app_data['keypairs'][keypair_id] = {
            'id': keypair_id,
            'algorithm': algorithm.value,
            'public_key': base64.b64encode(keypair.public_key).decode(),
            'private_key': base64.b64encode(keypair.private_key).decode(),
            'public_key_size': keypair.key_size_public,
            'private_key_size': keypair.key_size_private,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'keypair_id': keypair_id,
            'algorithm': algorithm.value,
            'public_key_size': keypair.key_size_public,
            'private_key_size': keypair.key_size_private,
            'public_key_preview': base64.b64encode(keypair.public_key)[:32].decode() + '...'
        })
        
    except Exception as e:
        logger.error(f"Error generating keypair: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sign-message', methods=['POST'])
def sign_message():
    """Sign a message using specified keypair"""
    try:
        data = request.get_json()
        keypair_id = data.get('keypair_id')
        message = data.get('message', '').encode()
        
        if keypair_id not in app_data['keypairs']:
            return jsonify({'error': 'Keypair not found'}), 404
        
        keypair_data = app_data['keypairs'][keypair_id]
        algorithm = None
        for alg in SignatureAlgorithm:
            if alg.value == keypair_data['algorithm']:
                algorithm = alg
                break
        
        # Decode private key
        private_key = base64.b64decode(keypair_data['private_key'])
        
        # Sign message
        signature_obj = sig_system.sign_message(message, private_key, algorithm)
        
        # Store signature
        signature_id = secrets.token_hex(8)
        app_data['signatures'][signature_id] = {
            'id': signature_id,
            'keypair_id': keypair_id,
            'algorithm': algorithm.value,
            'message': message.decode(),
            'signature': base64.b64encode(signature_obj.signature).decode(),
            'signature_size': signature_obj.signature_size,
            'timestamp': signature_obj.timestamp.isoformat()
        }
        
        return jsonify({
            'success': True,
            'signature_id': signature_id,
            'signature_size': signature_obj.signature_size,
            'algorithm': algorithm.value,
            'signature_preview': base64.b64encode(signature_obj.signature)[:32].decode() + '...'
        })
        
    except Exception as e:
        logger.error(f"Error signing message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-signature', methods=['POST'])
def verify_signature():
    """Verify a signature"""
    try:
        data = request.get_json()
        signature_id = data.get('signature_id')
        
        if signature_id not in app_data['signatures']:
            return jsonify({'error': 'Signature not found'}), 404
        
        signature_data = app_data['signatures'][signature_id]
        keypair_data = app_data['keypairs'][signature_data['keypair_id']]
        
        algorithm = None
        for alg in SignatureAlgorithm:
            if alg.value == signature_data['algorithm']:
                algorithm = alg
                break
        
        # Decode data
        message = signature_data['message'].encode()
        signature = base64.b64decode(signature_data['signature'])
        public_key = base64.b64decode(keypair_data['public_key'])
        
        # Verify signature
        is_valid = sig_system.verify_signature(message, signature, public_key, algorithm)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'algorithm': algorithm.value,
            'message': signature_data['message']
        })
        
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/benchmark', methods=['POST'])
def run_benchmark():
    """Run performance benchmark"""
    try:
        data = request.get_json()
        message_size = data.get('message_size', 1024)
        iterations = data.get('iterations', 10)
        
        # Run benchmark
        results = sig_system.benchmark_algorithms(message_size=message_size, iterations=iterations)
        app_data['benchmark_results'] = results
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error running benchmark: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-certificate', methods=['POST'])
def create_certificate():
    """Create a quantum-safe certificate"""
    try:
        data = request.get_json()
        subject_name = data.get('subject_name')
        algorithm_name = data.get('algorithm')
        validity_days = data.get('validity_days', 365)
        
        algorithm = None
        for alg in SignatureAlgorithm:
            if alg.value == algorithm_name:
                algorithm = alg
                break
        
        if not algorithm:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
        # Create certificate chain
        chain = sig_system.create_certificate_chain(subject_name, algorithm, validity_days)
        
        # Store certificate
        cert_id = secrets.token_hex(8)
        app_data['certificates'][cert_id] = {
            'id': cert_id,
            'subject_name': subject_name,
            'algorithm': algorithm.value,
            'valid_from': chain['subject_certificate'].valid_from.isoformat(),
            'valid_to': chain['subject_certificate'].valid_to.isoformat(),
            'serial_number': chain['subject_certificate'].serial_number,
            'chain_valid': chain['chain_valid'],
            'public_key_size': chain['subject_keypair'].key_size_public,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'certificate_id': cert_id,
            'subject_name': subject_name,
            'algorithm': algorithm.value,
            'valid_until': chain['subject_certificate'].valid_to.isoformat(),
            'chain_valid': chain['chain_valid']
        })
        
    except Exception as e:
        logger.error(f"Error creating certificate: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = {
        'total_keypairs': len(app_data['keypairs']),
        'total_signatures': len(app_data['signatures']),
        'total_certificates': len(app_data['certificates']),
        'supported_algorithms': len(list(SignatureAlgorithm)),
        'recent_keypairs': list(app_data['keypairs'].values())[-5:],
        'recent_signatures': list(app_data['signatures'].values())[-5:],
        'recent_certificates': list(app_data['certificates'].values())[-5:],
    }
    return jsonify(stats)

@app.route('/keypairs')
def keypairs():
    """Key pairs management page"""
    return render_template('keypairs.html', 
                         keypairs=app_data['keypairs'].values(),
                         algorithms=SignatureAlgorithm)

@app.route('/signatures')
def signatures():
    """Signatures management page"""
    return render_template('signatures.html', 
                         signatures=app_data['signatures'].values(),
                         keypairs=app_data['keypairs'])

@app.route('/certificates')
def certificates():
    """Certificates management page"""
    return render_template('certificates.html', 
                         certificates=app_data['certificates'].values(),
                         algorithms=SignatureAlgorithm)

@app.route('/benchmark')
def benchmark():
    """Performance benchmark page"""
    return render_template('benchmark.html', 
                         results=app_data['benchmark_results'])

@app.route('/crypto-agility')
def crypto_agility():
    """Crypto-agility demonstration page"""
    return render_template('crypto_agility.html', 
                         algorithms=SignatureAlgorithm)

@app.route('/api/crypto-agility-demo', methods=['POST'])
def crypto_agility_demo():
    """Run crypto-agility demonstration"""
    try:
        results = sig_system.crypto_agility_demo()
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Error running crypto-agility demo: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Starting Quantum-Safe Cryptography Dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
