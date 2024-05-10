# OS and python version
MacBook 2017 Pro

Python 3.11.7 (But it should be applicable to all Python versions)

# Program Structure
COMP3221_BlockchainNode.py is the main program

Other py files can be viewed as self-made libraries imported by COMP3221_BlockchainNode.py

generate_config.py will generate .txt config files for the nodes (which has already been included in the submission)

test.cmd, test.sh are used to launch all the nodes conveniently. (Seperately for windows and macOS)

test.ipynb contains all the codes to test the program, including call test.cmd or test.sh to launch the nodes, generate socket packets and send to the target node

# How to launch the nodes
For macOS, `bash test.sh`

For windows, run test.cmd

This will launch all the nodes with configs in 'tests' folder

# How to perform the test
Firsly launch all the nodes, they will connect to each other in local machine.

Secondly, in test.ipynb, modify the global settings, you won't need to modify this part if you are running on local machine, otherwise change the address to whatever address the node is listening on.

Then, in test.ipynb, run the chunk containing the pre-defined function, this function is used to send the transaction message

Finally, in test.ipynb, choose how do you prefer to send the transaction:
1. Directly send: You need to modify the message by yourself, this allows more freedom. But as you are unable to compute the signature by yourself, this method is limited and can only send pre-written messages
2. Generate keypair and Send: Run the chunks that generate keypair, generate message and then send. In this way you only need to modify the message and the nonce, the sender and the signature will be generated for you
   
Conclusion: launch nodes -> prepare setting and functions (run the pre-written chunks) in test.ipynb -> choose a sending method and send transaction -> check the result in the terminal

# Some testcases
1. Default Test: Correct nonce, correct sender, correct signature
2. Incorrect nonce (Use 'Generate keypair and Send')
3. Incorrect sender (Use 'Directly send')
4. Incorrect signature (Use 'Directly send')
5. One node crashes

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