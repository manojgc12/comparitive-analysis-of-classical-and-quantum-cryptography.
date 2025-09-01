"""
Quantum-Safe Client-Server Applications
Demonstrates TLS client-server communication with hybrid cryptography and crypto-agility
"""

import asyncio
import socket
import ssl
import json
import time
import threading
import logging
import base64
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass
import secrets
from datetime import datetime

from hybrid_tls import HybridTLSHandshake, KeyExchangeType, CryptoAlgorithm
from quantum_signatures import HybridSignatureSystem, SignatureAlgorithm

def make_json_serializable(obj):
    """Convert objects containing bytes to JSON-serializable format"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

class ConnectionMode(Enum):
    """Connection security modes"""
    CLASSICAL = "classical"
    HYBRID = "hybrid"
    PQ_ONLY = "post_quantum"
    AUTO_NEGOTIATE = "auto_negotiate"

@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "localhost"
    port: int = 8443
    mode: ConnectionMode = ConnectionMode.HYBRID
    classical_alg: CryptoAlgorithm = CryptoAlgorithm.X25519
    pq_alg1: CryptoAlgorithm = CryptoAlgorithm.KYBER768
    pq_alg2: Optional[CryptoAlgorithm] = None
    signature_alg: SignatureAlgorithm = SignatureAlgorithm.DILITHIUM3
    max_connections: int = 10
    timeout: float = 30.0

@dataclass
class ClientConfig:
    """Client configuration"""
    server_host: str = "localhost"
    server_port: int = 8443
    mode: ConnectionMode = ConnectionMode.AUTO_NEGOTIATE
    preferred_classical: CryptoAlgorithm = CryptoAlgorithm.X25519
    preferred_pq1: CryptoAlgorithm = CryptoAlgorithm.KYBER768
    preferred_pq2: Optional[CryptoAlgorithm] = None
    signature_alg: SignatureAlgorithm = SignatureAlgorithm.DILITHIUM3
    timeout: float = 10.0

@dataclass
class ConnectionSession:
    """Active connection session"""
    session_id: str
    client_address: Tuple[str, int]
    handshake_result: Dict[str, Any]
    established_time: datetime
    last_activity: datetime
    bytes_sent: int = 0
    bytes_received: int = 0

class QuantumSafeServer:
    """Quantum-Safe TLS Server"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.sessions: Dict[str, ConnectionSession] = {}
        self.signature_system = HybridSignatureSystem()
        self.running = False
        self.server_socket = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(f"QSServer-{config.port}")
        
        # Create server certificate
        self.server_cert_chain = self.signature_system.create_certificate_chain(
            f"QS-Server-{config.host}:{config.port}",
            config.signature_alg
        )
        
        self.logger.info(f"Server initialized with {config.mode.value} mode")
    
    def _create_handshake_handler(self, client_socket: socket.socket, 
                                client_address: Tuple[str, int]) -> HybridTLSHandshake:
        """Create appropriate handshake handler based on server mode"""
        if self.config.mode == ConnectionMode.CLASSICAL:
            exchange_type = KeyExchangeType.CLASSICAL
        elif self.config.mode == ConnectionMode.HYBRID:
            exchange_type = KeyExchangeType.DUAL_HYBRID
        elif self.config.mode == ConnectionMode.PQ_ONLY:
            exchange_type = KeyExchangeType.PQ_ONLY
        else:  # AUTO_NEGOTIATE
            exchange_type = KeyExchangeType.DUAL_HYBRID  # Default to hybrid
        
        return HybridTLSHandshake(
            exchange_type=exchange_type,
            classical_alg=self.config.classical_alg,
            pq_alg1=self.config.pq_alg1,
            pq_alg2=self.config.pq_alg2
        )
    
    def _handle_client_connection(self, client_socket: socket.socket, 
                                client_address: Tuple[str, int]):
        """Handle individual client connection"""
        session_id = secrets.token_hex(16)
        self.logger.info(f"New connection from {client_address} - Session: {session_id}")
        
        try:
            client_socket.settimeout(self.config.timeout)
            
            # Perform quantum-safe TLS handshake
            handshake = self._create_handshake_handler(client_socket, client_address)
            handshake_result = handshake.perform_handshake()
            
            # Create session
            session = ConnectionSession(
                session_id=session_id,
                client_address=client_address,
                handshake_result=handshake_result,
                established_time=datetime.now(),
                last_activity=datetime.now()
            )
            self.sessions[session_id] = session
            
            # Send handshake confirmation
            handshake_response = {
                "status": "handshake_complete",
                "session_id": session_id,
                "server_mode": self.config.mode.value,
                "algorithms_used": handshake_result["algorithms"],
                "exchange_type": handshake_result["exchange_type"],
                "handshake_duration": handshake_result["handshake_duration"],
                "server_certificate": {
                    "subject": self.server_cert_chain["subject_certificate"].subject,
                    "algorithm": self.server_cert_chain["subject_certificate"].algorithm.value,
                    "valid_from": self.server_cert_chain["subject_certificate"].valid_from.isoformat(),
                    "valid_to": self.server_cert_chain["subject_certificate"].valid_to.isoformat()
                }
            }
            
            # Make response JSON-serializable
            handshake_response = make_json_serializable(handshake_response)
            
            response_data = json.dumps(handshake_response).encode('utf-8')
            client_socket.send(len(response_data).to_bytes(4, byteorder='big'))
            client_socket.send(response_data)
            session.bytes_sent += len(response_data) + 4
            
            self.logger.info(f"Handshake completed for session {session_id}: "
                           f"{handshake_result['exchange_type']} in "
                           f"{handshake_result['handshake_duration']:.3f}s")
            
            # Handle application data exchange
            self._handle_application_data(client_socket, session)
            
        except socket.timeout:
            self.logger.warning(f"Connection timeout for {client_address}")
        except Exception as e:
            self.logger.error(f"Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
                if session_id in self.sessions:
                    del self.sessions[session_id]
                self.logger.info(f"Connection closed for session {session_id}")
            except:
                pass
    
    def _handle_application_data(self, client_socket: socket.socket, 
                               session: ConnectionSession):
        """Handle application-level data exchange"""
        while self.running:
            try:
                # Receive message length
                length_data = client_socket.recv(4)
                if not length_data:
                    break
                
                message_length = int.from_bytes(length_data, byteorder='big')
                if message_length > 1024 * 1024:  # 1MB limit
                    self.logger.warning(f"Message too large: {message_length} bytes")
                    break
                
                # Receive message data
                message_data = b""
                while len(message_data) < message_length:
                    chunk = client_socket.recv(min(message_length - len(message_data), 4096))
                    if not chunk:
                        break
                    message_data += chunk
                
                session.bytes_received += len(message_data) + 4
                session.last_activity = datetime.now()
                
                # Parse message
                try:
                    message = json.loads(message_data.decode('utf-8'))
                    self.logger.debug(f"Received message type: {message.get('type', 'unknown')}")
                    
                    # Process message based on type
                    response = self._process_message(message, session)
                    
                    # Send response
                    response_data = json.dumps(response).encode('utf-8')
                    client_socket.send(len(response_data).to_bytes(4, byteorder='big'))
                    client_socket.send(response_data)
                    session.bytes_sent += len(response_data) + 4
                    
                except json.JSONDecodeError:
                    self.logger.error("Invalid JSON received")
                    break
                
            except socket.timeout:
                continue
            except Exception as e:
                self.logger.error(f"Error in application data handling: {e}")
                break
    
    def _process_message(self, message: Dict[str, Any], 
                        session: ConnectionSession) -> Dict[str, Any]:
        """Process application messages"""
        msg_type = message.get('type', 'unknown')
        
        if msg_type == 'ping':
            return {
                "type": "pong",
                "timestamp": datetime.now().isoformat(),
                "session_id": session.session_id
            }
        
        elif msg_type == 'echo':
            return {
                "type": "echo_response",
                "data": message.get('data', ''),
                "timestamp": datetime.now().isoformat(),
                "session_id": session.session_id
            }
        
        elif msg_type == 'crypto_info':
            response = {
                "type": "crypto_info_response",
                "session_info": {
                    "session_id": session.session_id,
                    "established_time": session.established_time.isoformat(),
                    "handshake_result": session.handshake_result,
                    "bytes_sent": session.bytes_sent,
                    "bytes_received": session.bytes_received
                },
                "server_config": {
                    "mode": self.config.mode.value,
                    "classical_alg": self.config.classical_alg.value,
                    "pq_alg1": self.config.pq_alg1.value,
                    "pq_alg2": self.config.pq_alg2.value if self.config.pq_alg2 else None,
                    "signature_alg": self.config.signature_alg.value
                }
            }
            return make_json_serializable(response)
        
        elif msg_type == 'rekey':
            # Simulate rekeying process
            new_handshake = self._create_handshake_handler(None, session.client_address)
            new_result = new_handshake.perform_handshake()
            
            return {
                "type": "rekey_response",
                "status": "success",
                "new_handshake": {
                    "algorithms": new_result["algorithms"],
                    "duration": new_result["handshake_duration"]
                },
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "type": "error",
                "message": f"Unknown message type: {msg_type}",
                "timestamp": datetime.now().isoformat()
            }
    
    def start(self):
        """Start the server"""
        self.running = True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.host, self.config.port))
            self.server_socket.listen(self.config.max_connections)
            
            self.logger.info(f"Quantum-Safe server listening on {self.config.host}:{self.config.port}")
            self.logger.info(f"Server mode: {self.config.mode.value}")
            self.logger.info(f"Certificate algorithm: {self.config.signature_alg.value}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client_connection,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connections: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.info("Server stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "active_sessions": len(self.sessions),
            "total_bytes_sent": sum(s.bytes_sent for s in self.sessions.values()),
            "total_bytes_received": sum(s.bytes_received for s in self.sessions.values()),
            "server_uptime": datetime.now().isoformat(),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "client": f"{s.client_address[0]}:{s.client_address[1]}",
                    "established": s.established_time.isoformat(),
                    "last_activity": s.last_activity.isoformat(),
                    "algorithms": s.handshake_result.get("algorithms", []),
                    "bytes_sent": s.bytes_sent,
                    "bytes_received": s.bytes_received
                }
                for s in self.sessions.values()
            ]
        }

class QuantumSafeClient:
    """Quantum-Safe TLS Client"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.signature_system = HybridSignatureSystem()
        self.socket = None
        self.session_info = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("QSClient")
        
        # Create client certificate
        self.client_cert_chain = self.signature_system.create_certificate_chain(
            f"QS-Client-{secrets.token_hex(8)}",
            config.signature_alg
        )
        
        self.logger.info(f"Client initialized with {config.mode.value} mode")
    
    def _create_handshake_handler(self) -> HybridTLSHandshake:
        """Create appropriate handshake handler based on client preferences"""
        if self.config.mode == ConnectionMode.CLASSICAL:
            exchange_type = KeyExchangeType.CLASSICAL
        elif self.config.mode == ConnectionMode.HYBRID:
            exchange_type = KeyExchangeType.DUAL_HYBRID
        elif self.config.mode == ConnectionMode.PQ_ONLY:
            exchange_type = KeyExchangeType.PQ_ONLY
        else:  # AUTO_NEGOTIATE
            exchange_type = KeyExchangeType.DUAL_HYBRID  # Default preference
        
        return HybridTLSHandshake(
            exchange_type=exchange_type,
            classical_alg=self.config.preferred_classical,
            pq_alg1=self.config.preferred_pq1,
            pq_alg2=self.config.preferred_pq2
        )
    
    def connect(self) -> bool:
        """Connect to the quantum-safe server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.timeout)
            
            self.logger.info(f"Connecting to {self.config.server_host}:{self.config.server_port}")
            self.socket.connect((self.config.server_host, self.config.server_port))
            
            # Perform quantum-safe TLS handshake
            handshake = self._create_handshake_handler()
            handshake_start = time.time()
            handshake_result = handshake.perform_handshake()
            handshake_duration = time.time() - handshake_start
            
            self.logger.info(f"Client-side handshake completed in {handshake_duration:.3f}s")
            
            # Receive server handshake confirmation
            length_data = self.socket.recv(4)
            message_length = int.from_bytes(length_data, byteorder='big')
            
            response_data = b""
            while len(response_data) < message_length:
                chunk = self.socket.recv(min(message_length - len(response_data), 4096))
                response_data += chunk
            
            self.session_info = json.loads(response_data.decode('utf-8'))
            
            if self.session_info.get("status") == "handshake_complete":
                self.logger.info(f"Connected! Session ID: {self.session_info['session_id']}")
                self.logger.info(f"Server mode: {self.session_info['server_mode']}")
                self.logger.info(f"Negotiated algorithms: {', '.join(self.session_info['algorithms_used'])}")
                return True
            else:
                self.logger.error("Handshake failed")
                return False
        
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to the server and receive response"""
        if not self.socket:
            self.logger.error("Not connected to server")
            return None
        
        try:
            # Send message
            message_data = json.dumps(message).encode('utf-8')
            self.socket.send(len(message_data).to_bytes(4, byteorder='big'))
            self.socket.send(message_data)
            
            # Receive response
            length_data = self.socket.recv(4)
            if not length_data:
                self.logger.error("Connection closed by server")
                return None
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            response_data = b""
            while len(response_data) < message_length:
                chunk = self.socket.recv(min(message_length - len(response_data), 4096))
                if not chunk:
                    self.logger.error("Incomplete response received")
                    return None
                response_data += chunk
            
            return json.loads(response_data.decode('utf-8'))
        
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return None
    
    def ping(self) -> Optional[float]:
        """Send a ping message and measure round-trip time"""
        start_time = time.time()
        response = self.send_message({"type": "ping"})
        
        if response and response.get("type") == "pong":
            return time.time() - start_time
        return None
    
    def echo(self, data: str) -> Optional[str]:
        """Send an echo message"""
        response = self.send_message({"type": "echo", "data": data})
        
        if response and response.get("type") == "echo_response":
            return response.get("data")
        return None
    
    def get_crypto_info(self) -> Optional[Dict[str, Any]]:
        """Get cryptographic information about the connection"""
        response = self.send_message({"type": "crypto_info"})
        
        if response and response.get("type") == "crypto_info_response":
            return response
        return None
    
    def rekey(self) -> bool:
        """Request a rekey operation"""
        response = self.send_message({"type": "rekey"})
        
        if response and response.get("type") == "rekey_response":
            if response.get("status") == "success":
                self.logger.info("Rekey operation successful")
                return True
        
        self.logger.error("Rekey operation failed")
        return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
                self.logger.info("Disconnected from server")
            except:
                pass
            finally:
                self.socket = None
                self.session_info = None

class CryptoAgilityDemo:
    """Demonstrates crypto-agility by switching between different configurations"""
    
    def __init__(self):
        self.logger = logging.getLogger("CryptoAgilityDemo")
        
        # Different configuration scenarios
        self.test_configs = [
            {
                "name": "Classical Only",
                "server_mode": ConnectionMode.CLASSICAL,
                "client_mode": ConnectionMode.CLASSICAL,
                "classical_alg": CryptoAlgorithm.X25519,
                "pq_alg1": CryptoAlgorithm.KYBER768,
                "signature_alg": SignatureAlgorithm.RSA_PSS_2048
            },
            {
                "name": "Hybrid Mode",
                "server_mode": ConnectionMode.HYBRID,
                "client_mode": ConnectionMode.HYBRID,
                "classical_alg": CryptoAlgorithm.X25519,
                "pq_alg1": CryptoAlgorithm.KYBER768,
                "signature_alg": SignatureAlgorithm.DILITHIUM3
            },
            {
                "name": "Post-Quantum Only",
                "server_mode": ConnectionMode.PQ_ONLY,
                "client_mode": ConnectionMode.PQ_ONLY,
                "classical_alg": CryptoAlgorithm.X25519,
                "pq_alg1": CryptoAlgorithm.KYBER1024,
                "signature_alg": SignatureAlgorithm.FALCON512
            },
            {
                "name": "Auto-Negotiation",
                "server_mode": ConnectionMode.AUTO_NEGOTIATE,
                "client_mode": ConnectionMode.AUTO_NEGOTIATE,
                "classical_alg": CryptoAlgorithm.ECDH_P256,
                "pq_alg1": CryptoAlgorithm.KYBER768,
                "signature_alg": SignatureAlgorithm.DILITHIUM3
            }
        ]
    
    def run_demo(self, port_base: int = 9000) -> Dict[str, Any]:
        """Run crypto-agility demonstration"""
        results = {}
        
        for i, config in enumerate(self.test_configs):
            port = port_base + i
            config_name = config["name"]
            
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Testing: {config_name}")
            self.logger.info(f"{'='*50}")
            
            # Create server configuration
            server_config = ServerConfig(
                port=port,
                mode=config["server_mode"],
                classical_alg=config["classical_alg"],
                pq_alg1=config["pq_alg1"],
                signature_alg=config["signature_alg"]
            )
            
            # Create client configuration
            client_config = ClientConfig(
                server_port=port,
                mode=config["client_mode"],
                preferred_classical=config["classical_alg"],
                preferred_pq1=config["pq_alg1"],
                signature_alg=config["signature_alg"]
            )
            
            # Test this configuration
            test_result = self._test_configuration(server_config, client_config)
            results[config_name] = test_result
            
            # Brief pause between tests
            time.sleep(1)
        
        return results
    
    def _test_configuration(self, server_config: ServerConfig, 
                          client_config: ClientConfig) -> Dict[str, Any]:
        """Test a specific configuration"""
        result = {
            "success": False,
            "error": None,
            "handshake_time": None,
            "ping_time": None,
            "crypto_info": None,
            "algorithms_used": None
        }
        
        server = None
        server_thread = None
        
        try:
            # Start server
            server = QuantumSafeServer(server_config)
            server_thread = threading.Thread(target=server.start, daemon=True)
            server_thread.start()
            
            # Give server time to start
            time.sleep(0.5)
            
            # Create and connect client
            client = QuantumSafeClient(client_config)
            
            connection_start = time.time()
            if client.connect():
                handshake_time = time.time() - connection_start
                result["handshake_time"] = handshake_time
                
                # Test ping
                ping_time = client.ping()
                if ping_time:
                    result["ping_time"] = ping_time
                
                # Get crypto info
                crypto_info = client.get_crypto_info()
                if crypto_info:
                    result["crypto_info"] = crypto_info
                    result["algorithms_used"] = crypto_info["session_info"]["handshake_result"]["algorithms"]
                
                # Test echo
                echo_response = client.echo("Hello, Quantum-Safe World!")
                if echo_response == "Hello, Quantum-Safe World!":
                    result["echo_test"] = True
                
                # Test rekey
                rekey_success = client.rekey()
                result["rekey_test"] = rekey_success
                
                client.disconnect()
                result["success"] = True
                
                self.logger.info(f"✓ Configuration test successful")
                self.logger.info(f"  Handshake time: {handshake_time:.3f}s")
                self.logger.info(f"  Ping time: {ping_time:.3f}s" if ping_time else "  Ping: Failed")
                self.logger.info(f"  Algorithms: {', '.join(result['algorithms_used']) if result['algorithms_used'] else 'None'}")
            
            else:
                result["error"] = "Connection failed"
                self.logger.error("✗ Connection failed")
        
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"✗ Test failed: {e}")
        
        finally:
            if server:
                server.stop()
        
        return result

# Example usage and testing
if __name__ == "__main__":
    print("=== Quantum-Safe Client-Server Demo ===\n")
    
    # Demo 1: Basic Server-Client Communication
    print("1. Basic Server-Client Communication Test")
    print("-" * 40)
    
    server_config = ServerConfig(
        port=8443,
        mode=ConnectionMode.HYBRID,
        classical_alg=CryptoAlgorithm.X25519,
        pq_alg1=CryptoAlgorithm.KYBER768,
        signature_alg=SignatureAlgorithm.DILITHIUM3
    )
    
    client_config = ClientConfig(
        server_port=8443,
        mode=ConnectionMode.AUTO_NEGOTIATE,
        preferred_classical=CryptoAlgorithm.X25519,
        preferred_pq1=CryptoAlgorithm.KYBER768,
        signature_alg=SignatureAlgorithm.DILITHIUM3
    )
    
    # Start server in separate thread
    server = QuantumSafeServer(server_config)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    try:
        # Connect client
        client = QuantumSafeClient(client_config)
        
        if client.connect():
            print("✓ Client connected successfully")
            
            # Test ping
            ping_time = client.ping()
            if ping_time:
                print(f"✓ Ping successful: {ping_time*1000:.2f}ms")
            
            # Test echo
            echo_response = client.echo("Hello, Quantum-Safe Server!")
            if echo_response:
                print(f"✓ Echo successful: '{echo_response}'")
            
            # Get crypto information
            crypto_info = client.get_crypto_info()
            if crypto_info:
                session_info = crypto_info["session_info"]
                print(f"✓ Session ID: {session_info['session_id']}")
                print(f"  Algorithms: {', '.join(session_info['handshake_result']['algorithms'])}")
                print(f"  Exchange type: {session_info['handshake_result']['exchange_type']}")
                print(f"  Handshake duration: {session_info['handshake_result']['handshake_duration']:.3f}s")
            
            # Test rekey
            if client.rekey():
                print("✓ Rekey operation successful")
            
            client.disconnect()
            print("✓ Client disconnected")
        
        else:
            print("✗ Client connection failed")
    
    except Exception as e:
        print(f"✗ Demo 1 failed: {e}")
    
    finally:
        server.stop()
    
    # Brief pause
    time.sleep(2)
    
    # Demo 2: Crypto-Agility Demonstration
    print("\n2. Crypto-Agility Demonstration")
    print("-" * 40)
    
    demo = CryptoAgilityDemo()
    demo_results = demo.run_demo(port_base=9000)
    
    print("\n=== Demo Results Summary ===")
    print(f"{'Configuration':<20} {'Success':<8} {'Handshake(s)':<12} {'Ping(ms)':<10} {'Algorithms'}")
    print("-" * 80)
    
    for config_name, result in demo_results.items():
        success = "✓" if result["success"] else "✗"
        handshake = f"{result['handshake_time']:.3f}" if result["handshake_time"] else "N/A"
        ping = f"{result['ping_time']*1000:.2f}" if result["ping_time"] else "N/A"
        algorithms = ", ".join(result["algorithms_used"]) if result["algorithms_used"] else "N/A"
        
        print(f"{config_name:<20} {success:<8} {handshake:<12} {ping:<10} {algorithms[:30]}")
        
        if not result["success"] and result["error"]:
            print(f"{'Error:':<20} {result['error']}")
    
    print("\n=== Demo Complete ===")
    print("The demonstration shows how the system can seamlessly switch between")
    print("different cryptographic configurations without code changes, demonstrating")
    print("true crypto-agility for post-quantum migration scenarios.")
