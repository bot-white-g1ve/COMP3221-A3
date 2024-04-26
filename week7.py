from enum import Enum
import hashlib
import json
import re

sender_valid = re.compile('^[a-fA-F0-9]{64}$')

TransactionValidationError = Enum('TransactionValidationError', ['INVALID_JSON', 'INVALID_SENDER', 'INVALID_MESSAGE'])

def make_transaction(sender, message) -> str:
	return json.dumps({'sender': sender, 'message': message})

def validate_transaction(transaction: str) -> dict | TransactionValidationError:
	try:
		tx = json.loads(transaction)
	except json.JSONDecodeError:
		return TransactionValidationError.INVALID_JSON

	if not(tx.get('sender') and isinstance(tx['sender'], str) and sender_valid.search(tx['sender'])):
		return TransactionValidationError.INVALID_SENDER

	if not(tx.get('message') and isinstance(tx['message'], str) and len(tx['message']) <= 70 and tx['message'].isalnum()):
		return TransactionValidationError.INVALID_MESSAGE

	return tx


class Blockchain():
	def  __init__(self):
		self.blockchain = []
		self.pool = []
		self.new_block('0' * 64)

	def new_block(self, previous_hash=None):
		block = {
			'index': len(self.blockchain) + 1,
			'transactions': self.pool.copy(),
			'previous_hash': previous_hash or self.blockchain[-1]['current_hash'],
		}
		block['current_hash'] = self.calculate_hash(block)
		self.pool = []
		self.blockchain.append(block)

	def last_block(self):
		return self.blockchain[-1]

	def calculate_hash(self, block: dict) -> str:
		block_object: str = json.dumps({k: block.get(k) for k in ['index', 'transactions', 'previous_hash']}, sort_keys=True)
		block_string = block_object.encode()
		raw_hash = hashlib.sha256(block_string)
		hex_hash = raw_hash.hexdigest()
		return hex_hash

	def add_transaction(self, transaction: str) -> bool:
		if isinstance((tx := validate_transaction(transaction)), dict):
			self.pool.append(tx)
			return True
		return False
