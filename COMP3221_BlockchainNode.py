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
import math

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

def initialize_keypair():
    global private_key_bytes, public_key_bytes
    private_key_bytes, public_key_bytes = crypto.generate_keypair_bytes()
    d_print("initialize keypair", f"generates private and public bytes: {private_key_bytes}, {public_key_bytes}")
    global public_key_hex
    public_key_hex = crypto.publickey_bytes_to_hex(public_key_bytes)
    d_print("initialize keypair", f"public key transformed to hex: {public_key_hex}")


def validate(message):
    d_print("server_thread", f"receive message:\n{message}")

    error = validation.validate_message(message)
    if  error == validation.ValidationError.INVALID_JSON:
        d_print("server_thread", "A message with wrong format received")
        return "wrong format"
    
    if error == validation.ValidationError.VALID_TRANSACTION:
        d_print("server_thread", "A valid transaction received")
        return "valid transaction"
    
    elif error == validation.ValidationError.VALID_REQUEST:
        d_print("server_thread", "A valid block request received")
        return "valid block request"
    
    elif error == validation.ValidationError.INVALID_VALUES:
        d_print("server_thread", "A invalid block request received")
        return "invalid block request"

    else:
        d_print("server_thread", "A invalid transaction received")
        return "invalid transaction"
    

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
            
            response_validation = validate(message)

            if  response_validation == "valid transaction":

                # send response
                response = json.dumps({"response": True})
                client_socket.sendall(struct.pack("!H", len(response)) + response.encode())

                # add to the pool
                bc.add_transaction(message)
                print(bc.blockchain[-1])
                
            elif response_validation == "invalid transaction":
                response = json.dumps({"response": False})
                client_socket.sendall(struct.pack("!H", len(response)) + response.encode())
                
            elif response_validation == "valid block request":
                print("valid block request")
                proposal =  bc.new_block_proposal()

                try:
                    message = proposal
                    msg_str = json.dumps(message)
                    msg_bytes = msg_str.encode('utf8')
                    network.send_prefixed(client_socket, msg_bytes)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")

                # send a singal to trigger consensus
                # passive_active = True
                
            elif response == "invalid block request":
                pass

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
            print(f"Error connecting to {host}:{port}: {e}")
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



#-------------------------------------------------------------


def perform_consensus(proposed_block,index):
    consensus_values = {proposed_block}

    for k in range(max_failures + 1):
        # Broadcast current values to all other nodes
        broadcast_block_request(index)

        # Receive values from other nodes
        for conn in connections:
            # receive value 
            received_values = network.recv_prefixed(conn)
            consensus_values.update(received_values)

    
    # # After f + 1 rounds, decide on the minimum value
    # agreed_value = min(consensus_values)
    # return agreed_value

def consensus_pipeline():
    while True:
        # Check if the transaction pool is ready
        if not bc.pool and not consensus_routine:
            time.sleep(1) 
            continue

        if consensus_routine:
            proposal = bc.new_block_proposal
            print("perform consensus as case 2")
            exit(1)


        elif bc.pool:
            proposal = bc.new_block_proposal()
            print(f"start proposal with index {proposal['index']}")
            perform_consensus(proposal,proposal['index'])

            # after execute
            bc.pool.pop(0)
        
            
            print("FINISHED CONSENUS")


        # also consider other case
        

        

        # Reset the connection timeout for active nodes
        # reset_node_timeouts()


def broadcast_block_request(index):
    """Sends a message to all connected nodes."""
    with connections_lock:
        for sock in connections:
            try:
                message = {"type": "values","payload":index }
                msg_str = json.dumps(message)
                msg_bytes = msg_str.encode('utf8')
                network.send_prefixed(sock, msg_bytes)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
            


def reset_node_timeouts():
    """Reset timeouts for all active nodes."""
    with connections_lock:
        for sock in connections:
            sock.settimeout(None)

# --------------------------------------------------------
def start_node(server_port, node_list):
    threading.Thread(target=start_server, args=(server_port,)).start()
    start_client(node_list)
    threading.Thread(target=consensus_pipeline, daemon=True).start()


if __name__ == "__main__":
    d_print("main", f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    parser = argparse.ArgumentParser(description='Blockchain Node')
    parser.add_argument('port_server', type=port_server_type, help='The port number on which the server listens for incoming connections from other nodes and clients.')
    parser.add_argument('node_list', type=node_list_type, help='Port number')
    args = parser.parse_args()
    print(args.node_list)

    max_failures = math.ceil(len(args.node_list)+1) - 1

    consensus_routine = False

    d_print("main", "server start")

    initialize_keypair()

    bc = blockchain.Blockchain()
    d_print("main", "block chain initialize")
    
    # Global list to keep track of connections
    connections = []

    # Lock for handling access to the connections list
    connections_lock = threading.Lock()

    start_node(args.port_server,args.node_list)