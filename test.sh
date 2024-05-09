#!/bin/bash

# Specially designed for macOS
dir_path='/Users/advancedai/Desktop/UniIssue/comp3221/A3'

# Open a new terminal
osascript -e "tell application \"Terminal\" to do script \"cd $dir_path; python3 COMP3221_BlockchainNode.py 5000 test/A.txt\""
osascript -e "tell application \"Terminal\" to do script \"cd $dir_path; python3 COMP3221_BlockchainNode.py 5001 test/B.txt\""
osascript -e "tell application \"Terminal\" to do script \"cd $dir_path; python3 COMP3221_BlockchainNode.py 5002 test/C.txt\""
