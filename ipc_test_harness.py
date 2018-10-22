# class for injection dependency testing node_information.py off an active ETH node
import json
import ipc_socket


NODE_SYNCED = True


class IPCTestHarness(ipc_socket.GethInterface):

    def send(self):
        request_data = json.loads(self.request_data)
        if type(request_data) == dict:
            if request_data["method"] == "admin_nodeInfo":
                return json.load(open("geth_test_responses/admin_nodeInfo", "r"))
            elif request_data["method"] == "admin_peers":
                return json.load(open("geth_test_responses/admin_peers", "r"))
            elif request_data["method"] == "eth_gasPrice":
                return json.load(open("geth_test_responses/eth_gasPrice.json", "r"))
            elif request_data["method"] == "eth_getBlockByNumber":
                if "params" in request_data:
                    args = request_data["params"]
                    if type(args) is list:
                        if type(args[0]) is not str:
                            raise TypeError("Expected string for first param")
                        if args[0] is not "latest":
                            raise ValueError("First argument should only be 'latest'")
                        if type(args[1]) is not bool:
                            raise TypeError("Expected bool for second param")
                        if ars[1] is not False:
                            raise ValueError("Second argument should only by False")
                        return json.load(open("geth_test_responses/eth_getBlockByNumber.json", "r"))
                    else:
                        raise TypeError("Expected params list in request")
            elif request_data["method"] == "eth_syncing":
                if NODE_SYNCED:
                    return json.load(open("geth_syncing.json", "r"))
                else:
                    return json.load(open("geth_not_syncing.json", "r"))
            elif request_data["method"] == "eth_getBalance":
                args = request_data["params"]
                if type(args) is list:
                    if type(args[0]) is not str:
                        raise TypeError("Expected string for first param")
                    if type(args[1]) is not str:
                        raise TypeError("Expected string for second param")
                    if args[1] is not 'latest':
                        raise ValueError("Second argument should only be 'latest'")
                else:
                    raise TypeError("Expected parameter list in request data")
                return json.load(open("eth_getBalance.json", "r"))
            else:
                raise ValueError("Unsupported method")
        else:
            raise TypeError("Stream output did not JSON deserialize into expected object")
