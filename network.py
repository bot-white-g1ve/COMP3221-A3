import socket
import struct
import json

def recv_exact(sock: socket.socket, msglen):
	'''
	Used in recv_prefixed
	'''
	chunks = []
	bytes_recd = 0
	while bytes_recd < msglen:
		chunk = sock.recv(min(msglen - bytes_recd, 2048))
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	return b''.join(chunks)

def send_exact(sock: socket.socket, msg: bytes):
	'''
	Used in send_prefixed
	'''
	totalsent = 0
	while totalsent < len(msg):
		sent = sock.send(msg[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent

def recv_prefixed(sock: socket.socket):
	size_bytes = recv_exact(sock, 2)
	size = struct.unpack("!H", size_bytes)[0]
	if size == 0:
		raise RuntimeError("empty message")
	if size > 65535 - 2:
		raise RuntimeError("message too large")
	return recv_exact(sock, size)

def send_prefixed(sock: socket.socket, msg: bytes):
	'''
	Used in send
	'''
	size = len(msg)
	if size == 0:
		raise RuntimeError("empty message")
	if size > 65535 - 2:
		raise RuntimeError("message too large")
	size_bytes = struct.pack("!H", size)
	send_exact(sock, size_bytes + msg)

def send_transaction(address, msg: dict):
	'''
	msg is a json object being sent
	'''
	msg_str = json.dumps(msg)
	msg_bytes = msg_str.encode('utf8')
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host, port = address.split(':')
	client_socket.connect((host, int(port)))
	send_prefixed(client_socket, msg_bytes)