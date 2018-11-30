# Feeds peer data from JSON output into database
# NOT intended for use on an actual client node, peer dumps
# in raw json format should be used instead and pulled using
# rsync to a dedicated analysis DB machine

import MySQLdb
import json
import os
import datetime
import re
import sys

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWD = ""
MYSQL_NAME = "peer_analysis"

PROCESS_COUNT = 4

PEER_DATA_FILE_NAME_REGEX = re.compile("^peers_[0-9]{1,}.json$")

# Update this
SERVER_PEER_DATA_DIRECTORIES = {
    "Test": "peers_log/",
}


class InvalidPeer(Exception):
    """Raised when a method is called on an invalid node (node_id=-1)"""
    pass


class PeerInfoIngest:
    def __init__(self, server_name, json_file_directory, logger=None):
        self.server_name = server_name
        self.logger = logger
        self.json_file_directory = json_file_directory
        try:
            self._db = MySQLdb.connect(MYSQL_HOST,
                                       MYSQL_USER,
                                       MYSQL_PASSWD,
                                       MYSQL_NAME)
            c = self._db.cursor()
            c.execute("SELECT node_id FROM nodes WHERE identifier=%s", (server_name,))
            row = c.fetchone()
            if row:
                self.node_id = row[0]
            else:
                c.execute("INSERT INTO nodes (identifier) VALUES (%s)", (server_name,))
                self._db.commit()
                self.node_id = c.lastrowid
        except MySQLdb.Error as e:
            try:
                error_message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                error_message = "MySQL Error: %s" % (str(e),)

            if self.logger:
                self.logger.error(error_message)
            else:
                print(error_message)

    def get_latest_peer_connection(self):
        if self.node_id == -1:
            raise InvalidPeer
        sql = "SELECT captured FROM peer_connections WHERE node_id=%s ORDER BY connection_id DESC LIMIT 1"
        c = self._db.cursor()
        c.execute(sql, (self.node_id,))
        row = c.fetchone()
        if row:
            return row[0]
        return None

    def ingest_new_data(self, x):
        if self.node_id == -1:
            raise InvalidPeer
        latest_peer_connection = self.get_latest_peer_connection()
        all_files = os.listdir(self.json_file_directory)
        file_count = len(all_files)
        portion = file_count / PROCESS_COUNT
        offset = x * portion
        limit = offset + portion
        if limit >= file_count:
            limit = file_count - 1
        selected_files = all_files[offset:limit]
        for each_file in selected_files:
            if PEER_DATA_FILE_NAME_REGEX.match(each_file):
                timestamp = int(each_file.split("_")[1].split(".")[0])
                captured = datetime.datetime.fromtimestamp(timestamp)
                if latest_peer_connection and captured < latest_peer_connection:
                    continue
                else:
                    result = self.feed_json_file(each_file)
                    if result > 0:
                        print("Subprocess {0}: Added {1} peer connections to database.".format(os.getpid(), result))

    def feed_json_file(self, json_file_name):
        if not PEER_DATA_FILE_NAME_REGEX.match(json_file_name):
            return -1
        timestamp = int(json_file_name.split("_")[1].split(".")[0])
        captured = datetime.datetime.fromtimestamp(timestamp)
        json_data_file = open(self.json_file_directory + json_file_name, "r")
        json_data = json.load(json_data_file)
        json_data_file.close()
        c = self._db.cursor()
        try:
            for peer in json_data:
                enode = peer["enode"]
                id = peer["id"]
                remote_addr = peer["network"]["remoteAddress"]
                caps = json.dumps(peer["caps"])
                sql = "INSERT INTO peer_connections (enode,id,remote_address,caps,node_id,captured) "
                sql += "VALUES (%s,%s,%s,%s,%s,%s);"
                c.execute(sql, (enode, id, remote_addr, caps, self.node_id, captured))
            self._db.commit()
            return len(json_data)

        except MySQLdb.Error as e:
            try:
                error_message = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                error_message = "MySQL Error: %s" % (str(e),)

            if self.logger:
                self.logger.error(error_message)
            else:
                print(error_message)
        return -1


if __name__ == "__main__":
    if len(sys.argv) == 1:
        for x in range(0, PROCESS_COUNT):
            try:
                pid = os.fork()
                if pid > 0:
                    for each in SERVER_PEER_DATA_DIRECTORIES.keys():
                        node = PeerInfoIngest(each, SERVER_PEER_DATA_DIRECTORIES[each])
                        node.ingest_new_data(x)
            except OSError as err:
                print("Fork #{0} failed: {1}".format(x,err))



