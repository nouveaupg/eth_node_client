# removes peer json data older than 24 hours

import os
import datetime


def clean_peers():
    cutoff = datetime.datetime.today() - datetime.timedelta(hours=24)
    all_files = os.listdir(self.json_file_directory)
    counter = 0
    for each_file in all_files:
        if PEER_DATA_FILE_NAME_REGEX.match(each_file):
            timestamp = int(each_file.split("_")[1].split(".")[0])
            captured = datetime.datetime.fromtimestamp(timestamp)
            if captured > cutoff:
                continue
            target_file = self.json_file_directory + each_file
            print("Deleting " + target_file)
            os.remove(target_file)
            counter += 1
    print("Removed {0} peer json files.".format(counter))


if __name__ == "__main__":
    clean_peers()
