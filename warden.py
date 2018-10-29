import node_information
import logging
import urllib
import json
import time

if __name__ == '__main__':
    logger = logging.getLogger("warden")
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('warden.log')
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

    config_stream = open("config.json", "r")
    config_data = json.load(config_stream)
    config_stream.close()

    logger.info("Warden configuration loaded: {0} second polling interval.".format(config_data["polling_interval"]))
    node_monitor = node_information.NodeInfo(logger)

    while 1:
        output_dict = dict(peers=node_monitor.peers,
                           synchronized=node_monitor.synced,
                           latest_gas_price=node_monitor.gas_price,
                           name=node_monitor.name,
                           enode=node_monitor.enode,
                           latest_block=node_monitor.latest_block)
        if output_dict["synchronized"]:
            output_dict["blocks_behind"] = 0
        else:
            output_dict["blocks_behind"] = node_monitor.blocks_behind

        data = json.dumps(output_dict).encode('utf8')
        req = urllib.request.Request(config_data["api_endpoint"] + config_data["api_key"], data=data,
                                     headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            logger.info("Node information updated successfully.")
        else:
            logger.error("Error code from API update endpoint: {0}".format(response.getcode()))
        # delay for 5 minutes
        time.sleep(config_data["polling_interval"])
        node_monitor.update()

