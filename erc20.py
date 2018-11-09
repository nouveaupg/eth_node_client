from eth_abi.abi import encode_abi
import binascii
import json
import rpc_interface
import ipc_socket
import util


class ERC20Contract:
    def __init__(self, token_name=None, symbol=None, initial_supply=None, contract_address=None):
        binary_stream = open("erc20.abi", "r")
        self.erc20abi = json.load(binary_stream)
        binary_stream.close()

        binary_stream = open("erc20.bin", "r")
        self.erc20bin = json.load(binary_stream)
        binary_stream.close()

        self.config = util.load_config_from_file()
        self.token_name = token_name
        self.token_symbol = symbol
        self.initial_supply = initial_supply
        self.contract_address = contract_address
        # TODO: verify this
        if self.contract_address:
            self.published = True
        else:
            self.published = False

    def create_smart_contract(self):
        encoded_data = encode_abi(('uint256', 'string', 'string'),(self.initial_supply, self.token_name, self.token_symbol))
        hex_encoded_data = encoded_data.hex()
        object_data = '0x' + self.erc20bin["object"] + hex_encoded_data
        rpc = rpc_interface.RPCInterface()
        result = rpc.eth_send_transaction(config["account"], object_data)
        return result


if __name__ == '__main__':
        contract = ERC20Contract(token_name="Glosspoints", symbol="XSGP", initial_supply=50000)
        res = contract.create_smart_contract()
        ipc_socket.GethInterface(res)
        result = ipc.send()
        print(result)
