# singleton which monitors the status of the node

import json
import unittest
import ipc_socket
import rpc_interface
import util

CONFIG_FILE_NAME = "/root/eth_node_client/config.json"

UNIT_TESTING = False
if UNIT_TESTING:
    import ipc_test_harness


class NodeInfo:
    def __init__(self, logger):
        config_file = open(CONFIG_FILE_NAME, "r")
        self.config = json.load(config_file)
        config_file.close()
        self.logger = logger
        self.rpc_interface = rpc_interface.RPCInterface()
        self.enode = None
        self.name = None
        self.eth_node_id = None
        # useful statistics on RPC responsiveness
        # will at least tell us if it's connected to a test harness!
        self.total_rpc_calls = 0
        self.total_rpc_delay = 0
        self.gas_price = None
        self.synced = False
        self.blocks_behind = 0
        self.balance = 0
        self.peers = []
        self.latest_block = None
        self._admin_node_info()
        self.update()

    def update(self):
        result = self._eth_syncing()
        if result and self.synced:
            self._eth_gasPrice()
            self._admin_peers()
            self._getLatestBlock()
            self._getBalance()

    @property
    def output_request(self):
        output = {"synchronized": self.synced,
                  "peers": len(self.peers),
                  "gas_price": self.gas_price,
                  "balance": self.balance,
                  "blocks_behind": self.blocks_behind}
        for each in self.latest_block.keys():
            output["latest_block_" + each] = self.latest_block[each]
        return output

    def _admin_node_info(self):
        request_data = self.rpc_interface.get_node_info()
        if UNIT_TESTING:
            ipc = ipc_test_harness.IPCTestHarness(request_data)
        else:
            ipc = ipc_socket.GethInterface(request_data, self.config)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                result_data = response_data["result"]
                self.enode = result_data["enode"]
                self.name = result_data["name"]
                self.eth_node_id = result_data["id"]
                message = "Successful admin_nodeInfo IPC call: " + str(response_data["delay"]) + " seconds"
                if self.logger:
                    self.logger.info(message)
                else:
                    print(message)
                return True
        message = "admin_nodeInfo API call failed."
        if self.logger:
            self.logger.error(message)
        else:
            print(message)
        return False

    def _admin_peers(self):
        request_data = self.rpc_interface.get_peers()
        if UNIT_TESTING:
            ipc = ipc_test_harness.IPCTestHarness(request_data)
        else:
            ipc = ipc_socket.GethInterface(request_data, self.config)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                result_data = response_data["result"]
                self.peers = []
                for each in result_data:
                    self.peers.append(dict(enode=each["enode"],
                                           caps=each["caps"],
                                           id=each["id"],
                                           network=each["network"]))
                message = "Successful admin_Peers IPC call: " + str(response_data["delay"]) + " seconds"
                message += "(" + str(len(self.peers)) + " peers)"
                if self.logger:
                    self.logger.info(message)
                else:
                    print(message)
                return True
        message = "admin_peers IPC call failed."
        if self.logger:
            self.logger.error(message)
        else:
            print(message)
        return False

    def _eth_gasPrice(self):
        request_data = self.rpc_interface.eth_gas_price()
        if UNIT_TESTING:
            ipc = ipc_test_harness.IPCTestHarness(request_data)
        else:
            ipc = ipc_socket.GethInterface(request_data, self.config)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                gas_price = util.hex_to_dec(response_data["result"])
                self.gas_price = util.wei_to_ether(gas_price)
                message = "Successful eth_gasPrice IPC call: " + str(response_data["delay"]) + " seconds"
                if self.logger:
                    self.logger.info(message)
                else:
                    print(message)
                return True
        message = "eth_gasPrice IPC call failed."
        if self.logger:
            self.logger.error(message)
        else:
            print(message)
        return False

    def _getLatestBlock(self):
        request_data = self.rpc_interface.get_latest_block()
        if UNIT_TESTING:
            ipc = ipc_test_harness.IPCTestHarness(request_data)
        else:
            ipc = ipc_socket.GethInterface(request_data, self.config)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                result_data = response_data["result"]
                self.latest_block = {'gas_limit': util.hex_to_dec(result_data["gasLimit"]),
                                     'gas_used': util.hex_to_dec(result_data["gasUsed"]), 'hash': result_data["hash"],
                                     'number': util.hex_to_dec(result_data["number"]),
                                     'size': util.hex_to_dec(result_data["size"]),
                                     'timestamp': util.hex_to_dec(result_data["timestamp"]),
                                     'transaction_count': len(result_data["transactions"])}
                message = "Successful getBlockByNumber IPC call: " + str(response_data["delay"]) + " seconds"
                if self.logger:
                    self.logger.info(message)
                else:
                    print(message)
                return True
        message = "getBlockByNumber API call failed."
        if self.logger:
            self.logger.error(message)
        else:
            print(message)
        return False

    def _getBalance(self):
        request_data = self.rpc_interface.get_balance(self.config["account"])
        if UNIT_TESTING:
            ipc = ipc_test_harness.IPCTestHarness(request_data)
        else:
            ipc = ipc_socket.GethInterface(request_data, self.config)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay = response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                message = "Successful eth_getBalance IPC call: " + str(response_data["delay"]) + " seconds"
                if self.logger:
                    self.logger.info(message)
                else:
                    print(message)
                self.balance = util.wei_to_ether(util.hex_to_dec(response_data["result"]))
                return True
        message = "eth_getBalance API call failed."
        if self.logger:
            self.logger.error(message)
        else:
            print(message)
        return False

    def _eth_syncing(self):
        request_data = self.rpc_interface.check_sync()
        if UNIT_TESTING:
            ipc = ipc_test_harness.IPCTestHarness(request_data)
        else:
            ipc = ipc_socket.GethInterface(request_data, self.config)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                syncing = response_data["result"]
                if type(syncing) == dict:
                    highest_block = util.hex_to_dec(syncing["highestBlock"])
                    current_block = util.hex_to_dec(syncing["currentBlock"])
                    self.synced = False
                    self.blocks_behind = highest_block - current_block
                else:
                    self.synced = True
                    self.blocks_behind = 0
                message = "Successful eth_syncing API call: " + str(response_data["delay"]) + " seconds"
                if self.logger:
                    self.logger.info(message)
                else:
                    print(message)
                return True
        else:
            message = "eth_syncing API called failed."
            if self.logger:
                self.logger.error(message)
            else:
                print(message)
            return False


class NodeInfoUnitTests(unittest.TestCase):
    def test_admin_nodeInfo(self):
        node_info = NodeInfo(logger=None)
        self.assertTrue(node_info._admin_node_info())

    def test_eth_syncing(self):
        node_info = NodeInfo(logger=None)
        self.assertTrue(node_info._eth_syncing())

    def test_eth_getBalance(self):
        node_info = NodeInfo(logger=None)
        self.assertTrue(node_info._getBalance())

    def test_eth_gasPrice(self):
        node_info = NodeInfo(logger=None)
        self.assertTrue(node_info._eth_gasPrice())

    def test_admin_peers(self):
        node_info = NodeInfo(logger=None)
        self.assertTrue(node_info._admin_peers())

    def test_latest_block(self):
        node_info = NodeInfo(logger=None)
        self.assertTrue(node_info._getLatestBlock())


if __name__ == "__main__":
    unittest.main()
