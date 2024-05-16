import argparse
import network
import crypto
import socket
import validation
import threading
import blockchain
import time 
import struct
import json
import math
from debug import d_initial, d_print

port = 0



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

# Call validation functions and print out the outcome
def validate(message, peername):
    d_print("validate", f"receive message:{message}")

    error = validation.validate_message(message, sender_and_nonce)
    if  error == validation.ValidationError.INVALID_JSON:
        d_print("validate", "A message with wrong format received")
        return "wrong format"
    elif error == validation.ValidationError.INVALID_TYPE:
        d_print("validate", "A message with wrong type received")
        return "wrong format"
    
    if error == validation.ValidationError.VALID_TRANSACTION:
        d_print("validate", "A valid transaction received")
        return "valid transaction"
    elif error == validation.ValidationError.INVALID_SENDER:
        d_print("validate", "A transaction with wrong sender received")
        print(f"[NET] Received a transaction from node {peername}: {message['payload']}")
        print(f"[TX] Received an invalid transaction, wrong sender - {message['payload']}")
        return "invalid transaction"
    elif error == validation.ValidationError.INVALID_MESSAGE:
        d_print("validate", "A transaction with wrong message received")
        print(f"[NET] Received a transaction from node {peername}: {message['payload']}")
        print(f"[TX] Received an invalid transaction, wrong message - {message['payload']}")
        return "invalid transaction"
    elif error == validation.ValidationError.INVALID_NONCE:
        d_print("validate", "A transaction with wrong nonce received")
        print(f"[NET] Received a transaction from node {peername}: {message['payload']}")
        print(f"[TX] Received an invalid transaction, wrong nonce - {message['payload']}")
        return "invalid transaction"
    elif error == validation.ValidationError.INVALID_SIGNATURE:
        d_print("validate", "A transaction with wrong signature received")
        print(f"[NET] Received a transaction from node {peername}: {message['payload']}")
        print(f"[TX] Received an invalid transaction, wrong signature message - {message['payload']}")
        return "invalid transaction"
    
    if error == validation.ValidationError.VALID_REQUEST:
        d_print("validate", "A valid block request received")
        return "valid block request"
    elif error == validation.ValidationError.INVALID_VALUES:
        d_print("validate", "A invalid block request received")
        return "invalid block request"

    d_print("validate", "Unknown error")
    return "wrong format"

def handle_client_connection(client_socket):
    try:
        while True:
            message = client_socket.recv(2)
            if not message:
                break

            length = struct.unpack("!H", message)[0]
            message = network.recv_exact(client_socket,length)
            message = json.loads(message)

            d_print("handle_client_connection",f"From {client_socket.getpeername()}, Received message: {message}")
            
            response_validation = validate(message, client_socket.getpeername())

            if  response_validation == "valid transaction":
                print(f"[NET] Received a transaction from node {client_socket.getpeername()}: {message['payload']}")
    
                d_print("handle_client_connection", f"The received message is a transaction")

                # send response
                response = json.dumps({"response": True})
                client_socket.sendall(struct.pack("!H", len(response)) + response.encode())

                # add to the pool
                d_print("handle_client_connection", f"Add to transaction pool: {message}")
                bc.add_transaction(message)
                print(f"[MEM] Stored transaction in the transaction pool: {message['payload']['signature']}")
                d_print("handle_client_connection", f"current end of blcokchain: {bc.blockchain[-1]}")
                
                # update the nonce
                d_print("handle_client_connection", f"call update_nonce")
                update_nonce(message)
                d_print("handle_client_connection", f"after updating, current record of sender: {sender_and_nonce}")
                
            elif response_validation == "invalid transaction":
                
                response = json.dumps({"response": False})
                client_socket.sendall(struct.pack("!H", len(response)) + response.encode())
                
            elif response_validation == "valid block request":
                print(f"[BLOCK] Received a block request from node {client_socket.getpeername()}: {message['payload']}")
      
                request_index = message['payload']
                agreement_index = bc.blockchain[-1]['index']
        
                d_print("handle_client_connection", f"The received message is a block request")

                global consensus_routine
                global consensus_values

                d_print("handle_client_connection", f"the request index is {request_index}, the agreed index is {agreement_index}")
                # invalid index
                if request_index < 0 or request_index > agreement_index+1:
                    proposal = {}
                    d_print("handle_client_connection", f"The received block request's request index is in case1")
                
                # index already agreed
                elif request_index <= agreement_index:
                    proposal = [bc.blockchain[request_index]]
                    d_print("handle_client_connection", f"The received block request's request index is in case2")

                # consensus process
                elif request_index == agreement_index+1:
                    # Start consensus
                    if not consensus_values:
                        proposal =  [bc.new_block_proposal()]
                        d_print("handle_client_connection", "new consenus started!")
                        consensus_routine = True

                    # During consensus
                    elif consensus_values:
                        proposal = consensus_values
                        d_print("handle_client_connection", "consensus is going on!") 

                try:
                    message = proposal
                    msg_str = json.dumps(message)
                    msg_bytes = msg_str.encode('utf8')
                    network.send_prefixed(client_socket, msg_bytes)

                except Exception as e:
                    print(f"Error broadcasting message: {e}")

            elif response == "invalid block request":
                pass
    except Exception as e:
        print(f"{client_socket.getpeername()} is down")
    finally:
        client_socket.close()

# Update the nonce whenever receive a valid transaction
def update_nonce(message):
    sender = message['payload']['sender']
    d_print("update_nonce", f"The sender is {sender}")
    if sender in sender_and_nonce:
        sender_and_nonce[sender] += 1
        d_print("update_nonce", f"The sender has already sent previously, nonce incremented to {sender_and_nonce[sender]}")
    elif sender not in sender_and_nonce:
        sender_and_nonce[sender] = 0
        d_print("update_nonce", f"The sender has not sent previously, nonce start at {sender_and_nonce[sender]}")

# Listening (server) socket
def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        d_print("start_server", f"Server listening on host {server_socket.getsockname()}")
        
        while True:
            client_socket, address = server_socket.accept()
            d_print("start_server", f"Accepted connection from {address}")
            threading.Thread(target=handle_client_connection, args=(client_socket,)).start()


def manage_connection(host, port):
    while True:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            d_print("manage_connection", f"try to connect to {host}:{port}")
            sock.connect((host, port))
            with connections_lock:
                connections.append(sock)
            d_print("manage_connection", f"connect successfully to {host}:{port}")
            print(f"Connected to {host}:{port}")
            while True:
                time.sleep(10)

        except socket.error as e:
            d_print("manage_connection", f"Error connecting to {host}:{port}: {e}")
            pass

        finally:
            if sock:
                with connections_lock:
                    if sock in connections:
                        connections.remove(sock)
                sock.close()
            time.sleep(5)

# Create a thread for each client
def start_client(node_list):
    for host, port in node_list:
        threading.Thread(target=manage_connection, args=(host, port)).start()



def perform_consensus(proposed_block,index):
    global consensus_values
    consensus_values = [proposed_block]

    for k in range(max_failures + 1):
        # boradcast request values
        broadcast_block_request(index)

        # Receive values from other nodes
        try:    
            for conn in connections:
                message = conn.recv(2)
                if not message:
                    break
                    
                conn.settimeout(None)
                d_print("perform_consensus", "the timeout to a node is reset to inf")

                length = struct.unpack("!H", message)[0]
                message = network.recv_exact(conn,length)
                message = json.loads(message)

                d_print("perform_consensus",f"Received message: {message}")

                for block in message:
                    if block not in consensus_values:
                        consensus_values.append(block)
        except Exception:
            connections.remove(conn)


    d_print("perform_consensus", f"consensus value is {consensus_values}")

    # After f + 1 rounds, decide on the minimum value
    filtered_list = [item for item in consensus_values if item.get('transactions')]
    agreement = min(filtered_list, key=lambda x: x['current_hash'])
    print(f"[CONSENSUS] Appended to the blockchain: {agreement['current_hash']}")
    bc.blockchain.append(agreement)

    # clear the consensus values 
    consensus_values = []

# Keep checking if the pool is ready and perform corresponding operations
def consensus_pipeline():
    global consensus_routine
    while True:
        time.sleep(2)
        
        # Check if the transaction pool is ready

        if not bc.pool and not consensus_routine:
            continue
        
        if consensus_routine:
            d_print("consensus_pipeline", "perform consensus as case 2: ")

            proposal = bc.new_block_proposal()
            
            perform_consensus(proposal,proposal['index'])

            with consensus_lock:
                consensus_routine = False
            

        elif bc.pool:

            d_print("consensus_pipeline", "perform consensus as case 1: ")

            proposal = bc.new_block_proposal()
            print(f"[PROPOSAL] Created a block proposal: {proposal}")
            perform_consensus(proposal,proposal['index'])

            bc.pool.pop(0)

            with consensus_lock:
                consensus_routine = False

        # Reset the connection timeout for active nodes
        # reset_node_timeouts()


def broadcast_block_request(index):
    """Sends a message to all connected nodes."""
    with connections_lock:
        for sock in connections:
            try:
                d_print("broadcast_block_request", "the timeout to a node is set to 5 sec")
                sock.settimeout(5)

                message = {"type": "values","payload":index }
                msg_str = json.dumps(message)
                msg_bytes = msg_str.encode('utf8')
                network.send_prefixed(sock, msg_bytes)
                d_print("broadcast_block_request", "broadcast success")
            except Exception as e:
                d_print("broadcast_block_request", "error, attempt reconnect")
                attempt_reconnect(sock, msg_bytes)

def attempt_reconnect(sock, msg_bytes):
    try:
        host, port = sock.getpeername()
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_sock.connect((host, port))
        new_sock.settimeout(5)
        connections.remove(sock)
        connections.append(new_sock)
        network.send_prefixed(new_sock, msg_bytes)
        # d_print("attempt_reconnect", f"reconnection successful for {host}, {port}")
    except Exception as e:
        # d_print("attempt_reconnect", f"reconnection failed for {host}, {port}")
        try:
            if new_sock in connections:
                connections.remove(new_sock)
            if sock in connections:
                connections.remove(sock)
        except Exception:
            pass

def reset_node_timeouts():
    """Reset timeouts for all active nodes."""
    with connections_lock:
        for sock in connections:
            sock.settimeout(None)


# initialize every thread
def start_node(server_port, node_list):
    threading.Thread(target=start_server, args=(server_port,)).start()
    start_client(node_list)
    threading.Thread(target=consensus_pipeline).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Blockchain Node')
    parser.add_argument('port_server', type=port_server_type, help='The port number on which the server listens for incoming connections from other nodes and clients.')
    parser.add_argument('node_list', type=node_list_type, help='Port number')

    # config 
    args = parser.parse_args()

    # global variables
    port = args.port_server
    d_initial(port)
    
    max_failures = math.ceil((len(args.node_list)+1)/2) - 1
    d_print("main", f"node file is: {args.node_list}")
    d_print("main", f"max failures allowed : {max_failures}")

    consensus_routine = False
    consensus_values = []
    connections = []
    sender_and_nonce = {}
    
    # initialize
    initialize_keypair()
    bc = blockchain.Blockchain()


    # Locks to avoid data race
    connections_lock = threading.Lock()
    consensus_lock = threading.Lock()

    # testing
    d_print("main", "server start")

    start_node(args.port_server,args.node_list)