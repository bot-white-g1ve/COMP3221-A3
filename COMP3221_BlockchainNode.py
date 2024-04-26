import argparse
import network
import crypto
import socket
from datetime import datetime

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
                node_list.append(node)
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

def server_thread(port):
    host_ip = socket.gethostbyname(socket.gethostname())
    d_print("server_thread", f"find host_ip being {host_ip}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip, port))
    server_socket.listen()

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            message = network.recv_prefixed(client_socket)
            d_print("server_thread", f"receive message:\n{message}")
    except KeyboardInterrupt:
        d_print("server terminate")
    finally:
        server_socket.close()

if __name__ == "__main__":
    d_print("main", f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    parser = argparse.ArgumentParser(description='Blockchain Node')
    parser.add_argument('port_server', type=port_server_type, help='The port number on which the server listens for incoming connections from other nodes and clients.')
    parser.add_argument('node_list', type=node_list_type, help='Port number')
    args = parser.parse_args()

    d_print("main", "server start")

    initialize_keypair()

    server_thread(args.port_server)