from urllib.request import Request, urlopen, URLError
import node_information
import logging
import json
import time
import ssl
import util
from subprocess import call

CONSOLE_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.DEBUG

# WARNING: these get passed to subprocess.call(shell=True)

COMMAND_PY_PATH = "/home/ethereum/ERC20Interface/command.py"
PYTHON_CMD = "/usr/local/bin/python3"


class Warden:
    def __init__(self, use_logger=None):
        self.config = util.load_config_from_file()
        self.logger = use_logger
        if self.logger is None:
            self.logger = logging.getLogger("warden.worker")
            worker_fh = logging.FileHandler(self.config['log_file_path'])
            worker_fh.setLevel(FILE_LOG_LEVEL)
            worker_fh.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            # add the handlers to the logger
            self.logger = logger.addHandler(worker_fh)

    def start_update_loop(self):
        self._update_loop()

    def _update_loop(self):
        node_monitor = node_information.NodeInfo(self.logger)

        while 1:
            output_dict = node_monitor.output_request
            if output_dict["synchronized"]:
                output_dict["blocks_behind"] = 0
                data = json.dumps(output_dict).encode()
                ssl_context = ssl.SSLContext()
                ssl_context.load_default_certs()
                api_endpoint_url = config_data["api_endpoint"] + config_data["api_key"]

                logger.debug("Making request to api_endpoint: " + api_endpoint_url)

                req = Request(api_endpoint_url,
                              data=data,
                              headers={'Content-Type': 'application/json',
                                       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'},
                              method="POST")
                try:
                    response = urlopen(req, context=ssl_context)
                    json_data = json.loads(response.read())
                    directed_commands = json_data["directed_commands"]
                    undirected_commands = json_data["undirected_commands"]
                    logger.info("Update accepted from Node API. Command queue: {0} undirected, {1} directed".format(
                        undirected_commands,
                        directed_commands))
                    if undirected_commands > 0:
                        call("{0} {1} undirected_command".format(PYTHON_CMD, COMMAND_PY_PATH, ), shell=True)
                except URLError as err:
                    logger.error("Error from Node Update API update endpoint: {0}".format(err))
                    error_delay = config_data['polling_interval']
                    logger.info("Sleeping for {0} seconds".format(error_delay))
                    time.sleep(error_delay)
                except KeyError as err:
                    error_delay = config_data['polling_interval']
                    logger.info(
                        "Did not receive commands from Node Update API, sleeping for {0} seconds.".format(error_delay))
                    time.sleep(error_delay)
            else:
                logger.info("Syncing: {0} blocks behind".format(node_monitor.blocks_behind))
                output_dict["blocks_behind"] = node_monitor.blocks_behind
                # slow down the warden when the node is unsynchronized to
                # reduce app server load
                error_delay = config_data['polling_interval']
                logger.info("Sleeping for {0} seconds".format(error_delay))
                time.sleep(error_delay)
            self._update_loop()


if __name__ == '__main__':
    print("Warden v3 started.")
    print("Loading configuration from:" + util.DEFAULT_CONFIG_PATH)
    config_data = util.load_config_from_file()
    if config_data is None:
        print("Could not open configuration file.")
        exit(1)

    logger = logging.getLogger("warden")
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(config_data["log_file_path"])
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("Warden v3: logging initialized")
    warden = Warden(use_logger=logger)
    warden.start_update_loop()