# singleton which monitors the status of the node

import ipc_socket
import ipc_test_harness
import rpc_interface
import sqlite3
import json
import util


class NodeInfo:
    def __init__(self, logger):
        self.config = json.read(open("config.json", "r"))
        self.logger = logger
        # initalize memory db
        self.db = sqlite3.connect(":memory:")
        schema_file = open("sqlite_mem_table_schema.sql")
        schema = schema_file.read()
        self.db.execute(schema)

        self.rpc_interface = rpc_interface.RPCInterface()
        self.enode = None
        self.name = None
        self.eth_node_id = None
        # useful statistics on RPC responsiveness
        # will at least tell us if it's connected to a test harness!
        self.total_rpc_calls = 0
        self.total_rpc_delay = 0
        self.gas_price = None

    def _admin_node_info(self):
        request_data = self.rpc_interface.get_node_info()
        ipc = ipc_test_harness.IPCTestHarness(request_data)
        response_data = ipc.send()

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                result_data = response_data["result"]
                self.enode = result_data["enode"]
                self.name = result_data["name"]
                self.eth_node_id = result_data["id"]
                self.logger.info("Successful admin_nodeInfo IPC call: " + response_data["delay"] + " seconds")
                return True
        self.logger.error("admin_nodeInfo API call failed.")
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
        response_data = ipc.send()

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                gas_price = util.hex_to_dec(response_data["result"])
                self.gas_price = util.wei_to_ether(gas_price)
                self.logger.info("Successful eth_gasPrice IPC call: " + response_data["delay"] + " seconds")
        self.logger.error("eth_gasPrice IPC call failed.")
        return False

    def _getLatestBlock(self):
        request_data = self.rpc_interface.get_latest_block()
        ipc = ipc_test_harness.IPCTestHarness(request_data)
        response_data = ipc.send()

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
        response_data = ipc.send()

        if type(response_data) == dict:
            self.total_rpc_delay == response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                self.logger.info("Successful eth_getBalance IPC call: " + response_data["delay"] + " seconds")
                return True
        self.logger.error("eth_getBalance API call failed.")
        return False

    def _eth_syncinging(self):
        request_data = self.rpc_interface.check_sync()
        ipc = ipc_test_harness.IPCTestHarness(request_data)
        response_data = ipc.send()

        if type(response_data) == dict:
            self.total_rpc_delay += response_data["delay"]
            self.total_rpc_calls += 1
            if "result" in response_data:
                self.logger.info("Successful eth_syncing API call: " + response_data["delay"] + " seconds")
