# Default Test Result
Node A:
[NET] Received a transaction from node ('127.0.0.1', 63776): {'sender': 'a57819938feb51bb3f923496c9dacde3e9f667b214a0fb1653b6bfc0f185363b', 'message': 'hello', 'nonce': 0, 'signature': '142e395895e0bf4e4a3a7c3aabf2f59d80c517d24bb2d98a1a24384bc7cb29c9d593ce3063c5dd4f12ae9393f3345174485c052d0f5e87c082f286fd60c7fd0c'}
[MEM] Stored transaction in the transaction pool: 142e395895e0bf4e4a3a7c3aabf2f59d80c517d24bb2d98a1a24384bc7cb29c9d593ce3063c5dd4f12ae9393f3345174485c052d0f5e87c082f286fd60c7fd0c
[PROPOSAL] Created a block proposal: {'index': 1, 'transactions': [{'sender': 'a57819938feb51bb3f923496c9dacde3e9f667b214a0fb1653b6bfc0f185363b', 'message': 'hello', 'nonce': 0, 'signature': '142e395895e0bf4e4a3a7c3aabf2f59d80c517d24bb2d98a1a24384bc7cb29c9d593ce3063c5dd4f12ae9393f3345174485c052d0f5e87c082f286fd60c7fd0c'}], 'previous_hash': '3e84ae1bd33c5be169869f3c4ce425e51e4d9c41cff1b310ecf5b6d2e83c2941', 'current_hash': '99d708e1c447bf022b1917ddd9416873d16b4797ad261dd66b1608d010f38dfb'}
[CONSENSUS] Appended to the blockchain: 99d708e1c447bf022b1917ddd9416873d16b4797ad261dd66b1608d010f38dfb
[BLOCK] Received a block request from node ('127.0.0.1', 63764): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63764): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63766): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63766): 1

Node B:
[BLOCK] Received a block request from node ('127.0.0.1', 63771): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63771): 1
[CONSENSUS] Appended to the blockchain: 99d708e1c447bf022b1917ddd9416873d16b4797ad261dd66b1608d010f38dfb
[BLOCK] Received a block request from node ('127.0.0.1', 63767): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63767): 1

Node C:
[BLOCK] Received a block request from node ('127.0.0.1', 63772): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63772): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63773): 1
[BLOCK] Received a block request from node ('127.0.0.1', 63773): 1
[CONSENSUS] Appended to the blockchain: 99d708e1c447bf022b1917ddd9416873d16b4797ad261dd66b1608d010f38dfb

Analysis:
1. A received a transaction -> A created a block proposal -> A requested blocks from other nodes -> A decided -> A received block request from B (two times because of consensus protocol) -> A received block request from C
2. B received block request from A -> B requested blocks from other nodes -> B decided -> B received block request from C
3. C received block request from A -> C received blocks from B -> C requested blocks from other nodes -> C decided