import argparse
import network
import crypto
import socket
import validation
from datetime import datetime
import threading
import blockchain
import time 
import struct
import json

def d_print(func, str):
    with open('debug.txt', 'a') as f:
        f.write(f"(In {func}) {str}\n")

def port_server_type(port_server):
    '''
    Validate port_server argument
    '''
    port_server = int(port_server)
    return port_server

def node_list_type(node_list_file):
    '''
    Validate node_list argument
    '''
    node_list = []
    try:
        with open(node_list_file, 'r') as f:
            for line in f:
                node = line.strip("\n")
                ip, port = node.split(":")
                node_list.append((ip,int(port)))
    except FileNotFoundError:
        d_print("node_list_type", f"node list file {node_list_file} is not found")
        raise FileNotFoundError(f"node list file {node_list_file} is not found")
    return node_list



def validate(message):
    d_print("server_thread", f"receive message:\n{message}")
    if validation.validate_message(message) == validation.ValidationError.INVALID_JSON:
        d_print("server_thread", "A message with wrong format received")
    elif validation.validate_message(message) == validation.ValidationError.INVALID_TYPE:
        d_print("server_thread", "A message with wrong type received")
    elif validation.validate_message(message) == validation.ValidationError.INVALID_SENDER:
        d_print("server_thread", "A transaction with wrong sender received")
    elif validation.validate_message(message) == validation.ValidationError.INVALID_MESSAGE:
        d_print("server_thread", "A transaction with wrong message received")
    elif validation.validate_message(message) == validation.ValidationError.INVALID_NONCE:
        d_print("server_thread", "A transaction with wrong nonce received")
    elif validation.validate_message(message) == validation.ValidationError.INVALID_SIGNATURE:
        d_print("server_thread", "A transaction with wrong signature received")
    elif validation.validate_message(message) == validation.ValidationError.INVALID_VALUES:
        d_print("server_thread", "A block request with wrong values received")

    elif validation.validate_message(message) == validation.ValidationError.VALID_TRANSACTION:
        d_print("server_thread", "A valid transaction received")
        return 1
    elif validation.validate_message(message) == validation.ValidationError.VALID_REQUEST:
        d_print("server_thread", "A valid block request received")
        return 2
    
    return 0


def initialize_keypair():
    global private_key_bytes, public_key_bytes
    private_key_bytes, public_key_bytes = crypto.generate_keypair_bytes()
    d_print("initialize keypair", f"generates private and public bytes: {private_key_bytes}, {public_key_bytes}")
    global public_key_hex
    public_key_hex = crypto.publickey_bytes_to_hex(public_key_bytes)
    d_print("initialize keypair", f"public key transformed to hex: {public_key_hex}")

def handle_client_connection(client_socket):
    try:
        while True:
            message = client_socket.recv(2)
            if not message:
                break

            length = struct.unpack("!H", message)[0]
            message = network.recv_exact(client_socket,length)
            message = json.loads(message)

            print(f"Received message: {message}")
            
            # tranasctions
            if validate(message) == 1:
                print(bc.blockchain[-1])
                bc.add_transaction(message)
                bc.new_block()
                print(bc.blockchain[-1])
                
                
            elif validate(message) == 2:
              pass

            else:
                print("Invalid message received")

    finally:
        client_socket.close()

def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        print(f"Server listening on port {port}...")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"Accepted connection from {address}")
            threading.Thread(target=handle_client_connection, args=(client_socket,)).start()

def manage_connection(host, port):
    while True:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            with connections_lock:
                connections.append(sock)
            print(f"Connected to {host}:{port}")
            while True:
                time.sleep(10)
        except socket.error as e:
            pass
            # print(f"Error connecting to {host}:{port}: {e}")
        finally:
            if sock:
                with connections_lock:
                    if sock in connections:
                        connections.remove(sock)
                sock.close()
            time.sleep(5)

def start_client(node_list):
    for host, port in node_list:
        threading.Thread(target=manage_connection, args=(host, port)).start()

def broadcast_message(message):
    """Sends a message to all connected nodes."""
    with connections_lock:
        for sock in connections:
            try:
                sock.sendall(message.encode())
            except socket.error as e:
                 print(f"Error sending message to {sock.getpeername()}: {e}")
            

def start_node(server_port, node_list):
    threading.Thread(target=start_server, args=(server_port,)).start()
    start_client(node_list)


if __name__ == "__main__":
    d_print("main", f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    parser = argparse.ArgumentParser(description='Blockchain Node')
    parser.add_argument('port_server', type=port_server_type, help='The port number on which the server listens for incoming connections from other nodes and clients.')
    parser.add_argument('node_list', type=node_list_type, help='Port number')
    args = parser.parse_args()
    print(args.node_list)

    d_print("main", "server start")

    initialize_keypair()

    bc = blockchain.Blockchain()
    d_print("main", "block chain initialize")
    
    # Global list to keep track of connections
    connections = []

    # Lock for handling access to the connections list
    connections_lock = threading.Lock()

    start_node(args.port_server,args.node_list)