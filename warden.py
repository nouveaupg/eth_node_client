import node_information
import logging
import json
import sys

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

    if len(sys.argv) == 2:
        api_key = sys.argv[1]
    else:
        logger.error("No API key specified!")
        sys.exit(1)

    config_stream = open("config.json", "r")
    config_data = json.load(config_stream)
    config_stream.close()

    logger.info("Warden configuration loaded: {0} second polling interval.".format(config_data["polling_interval"]))
    node_information.NodeInfo(logger)

    while 1:
        output_dict = dict(peers=node_information.peers,
                           synchronized=node_information.synced,
                           latest_gas_price=node_information.gas_price,
                           name=node_information.name,
                           enode=node_information.enode,
                           latest_block=node_information.latest_block)
        if output_dict["synchronized"]:
            output_dict["blocks_behind"] = 0
        else:
            output_dict["blocks_behind"] = node_information.blocks_behind

        data = json.dumps(output_dict).encode('utf8')
        req = urllib.request.Request(conditionsSetURL, data=data,
                                     headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            logger.info("Node information updated successfully.")
        else:
            logger.error("Error code from API update endpoint: {0}".format(response.getcode()))

        node_information.update()

