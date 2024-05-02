import hashlib
import json

class Blockchain:
    def __init__(self):
        self.blockchain = []
        self.pool = []
        self.create_genesis_block() 

    def create_genesis_block(self):
        # Initialize the genesis block
        genesis_block = {
            'index': 1,
            'transactions': [],
            'previous_hash': '0' * 64,
            'current_hash': None
        }
        genesis_block['current_hash'] = self.calculate_hash(genesis_block)
        self.blockchain.append(genesis_block)

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
        block_object = json.dumps({k: block.get(k) for k in ['index', 'transactions', 'previous_hash']}, sort_keys=True)
        block_string = block_object.encode()
        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()
        return hex_hash

    def add_transaction(self, transaction: dict):
        self.pool.append(transaction)
    