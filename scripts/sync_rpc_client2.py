# Python2 syncing state utility script
# run as root to determine state of ETH node synchronization
import json
import socket

data = {"jsonrpc": "2.0", "method": "eth_syncing", "params": [], "id": 1}


def setup_socket():
    new_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    new_socket.connect("/home/ethereum/.ethereum/geth.ipc")
    new_socket.settimeout(2)
    return new_socket


_socket = setup_socket()
_socket.sendall(json.dumps(data))
response_raw = ""

for _ in range(3):
    while True:
        try:
            response_raw += _socket.recv(4096)
        except socket.timeout:
            break
    if response_raw == "":
        _socket.close()
        _socket = setup_socket()
    break

response_data = json.loads(response_raw)
if "result" in response_data:
    syncing = response_data["result"]
    if type(syncing) is dict:
        current_block = int(syncing["currentBlock"], 16)
        highest_block = int(syncing["highestBlock"], 16)
        print "Syncing: %i blocks behind (%0.2f%%)" % (highest_block - current_block, (float(current_block) / float(highest_block) * 100.0))
    else:
        print "Synchronized."
