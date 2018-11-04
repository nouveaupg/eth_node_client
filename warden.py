from threading import Thread
from urllib.request import Request, urlopen
import node_information
import logging
import json
import time
import ssl
import os
import sys

CONSOLE_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.DEBUG
CONFIG_FILE_NAME = "/root/eth_node_client/config.json"
WARDEN_LOG_PATH = "/root/warden.log"


def load_config_from_file(filename):
    try:
        fp = open(filename, "r")
        json_data = json.load(fp)
        fp.close()
        return json_data
    except IOError as e:
        if e.errno == 2:
            return None


def check_for_updates(force):
    return force


class WardenThread(Thread):

    def run(self):
        config_data = load_config_from_file(CONFIG_FILE_NAME)
        if config_data is None:
            return
        logger = logging.getLogger("warden.thread")
        # create file handler which logs even debug messages
        thread_fh = logging.FileHandler(config_data["log_file_path"])
        thread_fh.setLevel(FILE_LOG_LEVEL)
        # create formatter and add it to the handlers
        thread_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        thread_fh.setFormatter(thread_formatter)
        # add the handlers to the logger
        logger.addHandler(thread_fh)

        logger.info("Warden worker thread (tid:{0}) loaded: {1} second polling interval.".format(self.ident, config_data["polling_interval"]))
        node_monitor = node_information.NodeInfo(logger)

        while 1:
            output_dict = node_monitor.output_request
            peer_count = len(node_monitor.peers)
            peer_log_file_name = "peers_log/peers_{0}.json".format(int(time.time()))
            peer_log = open(peer_log_file_name, "w")
            json.dump(node_monitor.peers, peer_log)
            peer_log.close()
            logger.debug("Wrote the {0} current peers to {1}".format(peer_count, peer_log_file_name))
            if output_dict["synchronized"]:
                output_dict["blocks_behind"] = 0
            else:
                output_dict["blocks_behind"] = node_monitor.blocks_behind

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
            response = urlopen(req, context=ssl_context)
            if response.getcode() == 200:
                logger.info("Node information updated successfully.")
            else:
                logger.error("Error code from API update endpoint: {0}".format(response.getcode()))
            # delay for 5 minutes
            polling_interval = config_data["polling_interval"]
            logger.info("Resting for {0} seconds".format(polling_interval))
            time.sleep(polling_interval)
            node_monitor.update()


if __name__ == '__main__':
    print("Warden v1 started.")
    print("Loading configuration from:" + CONFIG_FILE_NAME)
    config_data = load_config_from_file(CONFIG_FILE_NAME)
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

    # TODO: maybe this would be a use for some sort of git module?
    #
    # print("checking server for updates...")
    # if config_data:
    #     updated = check_for_updates(false)
    # else:
    #     updated = check_for_updates(true)
    # if updated:
    #     logger.info("successfully installed update from server.")
    # else:
    #     logger.info("update not installed.")
    #     if config_data is none:
    #         fatal_error("could not find config file or download from update.")
    # fh.close()

    daemonize = config_data["daemonize"]

    warden = WardenThread()
    if daemonize:
        warden.setDaemon(True)
    warden.start()

    if daemonize:
        # This doesn't currently work
        logger.info("Attempting to daemonize the warden process.")
        try:
            pid = os.fork()
            if pid > 0:
                # exit the launching process
                sys.exit(0)
        except OSError as err:
            logger.fatal('_Fork #1 failed: {0}'.format(err))
            sys.exit(1)
        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            logger.info('_Fork #2 failed: {0}'.format(err))
            sys.exit(1)
        # redirect standard file descriptors
        pid = os.getpid()
        logger.info("Launched master process, kill pid: {0} to terminate.".format(pid))
        pid_file = open("/tmp/warden.pid", "w")
        pid_file.write(str(pid))
        pid_file.close()
        sys.stdout.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'w')
        se = open(os.devnull, 'w')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # TODO: spawn watchdog process

    else:
        logger.info("Not daemonizing this process, you can change this in the configuration file.")


