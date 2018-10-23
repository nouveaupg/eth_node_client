# python 2 compatible utility for getting the gas price from a geth node in a human readable format
# retained for historical reasons
# October 19, 2018
import json
import socket


def wei_to_ether(wei):
    return 1.0 * wei / 10**18


data = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}

def setup_socket():
    new_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    new_socket.connect("/home/ethereum/.ethereum/geth.ipc")
    new_socket.settimeout(2)
    return new_socket


_socket = setup_socket()
_socket.sendall(json.dumps(data).encode())
response_raw = ""

for _ in range(3):
    while True:
        try:
            response_raw += _socket.recv(4096).decode()
        except socket.timeout:
            break
    if response_raw == "":
        _socket.close()
        _socket = setup_socket()
    break

response = json.loads(response_raw)
result = wei_to_ether(int(response['result'],16))
# probably better to keep in scientific/engineering notation
print("Gas Price: " + str(result) + " ETH")