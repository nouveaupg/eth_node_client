import ipc_socket
import rpc_interface
import sqlite3
import json


class NodeInfo:
    def __init__(self):
        self.config = json.read(open("config.json","r"))
        self.db = sqlite3.connect(":memory:")
        self.rpc_interface = rpc_interface.RPCInterface()

    def _get_node_info(self):
