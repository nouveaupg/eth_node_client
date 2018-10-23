# singleton which monitors the status of the node

import ipc_socket
import ipc_test_harness
import rpc_interface
import sqlite3
import json
import util
import unittest


class NodeInfo:
    def __init__(self, logger):
        config_file = open("config.json", "r")
        self.config = json.load(config_file)
        config_file.close()
        self.logger = logger
        # initalize memory db
        self.db = sqlite3.connect(":memory:")
        schema_file = open("sqlite_mem_table_schema.sql")
        schema = schema_file.read()
        schema_file.close()
        self.db.execute(schema)

        # TODO: peer db

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

    def _admin_node_info(self):
        request_data = self.rpc_interface.get_node_info()
        ipc = ipc_test_harness.IPCTestHarness(request_data)
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
        ipc = ipc_test_harness.IPCTestHarness(request_data)
        response_data = ipc.send()

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if result in response_data:
                result_data = response_data["result"]
                # TODO: feed into peer database
                self.logger.info("Successful admin_Peers IPC call: " + response_data["delay"] + " seconds")
                return True
        self.logger.error("admin_peers IPC call failed.")
        return False

    def _eth_gasPrice(self):
        request_data = self.rpc_interface.eth_gas_price()
        ipc = ipc_test_harness.IPCTestHarness(request_data)
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
        ipc = ipc_test_harness.IPCTestHarness(request_data)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                result_data = response_data["result"]

                # TODO: feed into memory database
                self.logger.info("Successful getBlockByNumber IPC call: " + response_data["delay"] + " seconds")
                return True
        self.logger.error("getBlockByNumber API call failed.")
        return False

    def _getBalance(self):
        request_data = self.rpc_interface.get_balance(self.config["account"])
        ipc = ipc_test_harness.IPCTestHarness(request_data)
        response_stream = ipc.send()
        response_data = self.rpc_interface.process_response(response_stream)

        if type(response_data) == dict:
            self.total_rpc_delay == response_data["delay"]
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
        ipc = ipc_test_harness.IPCTestHarness(request_data)
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

if __name__ == "__main__":
    unittest.main()