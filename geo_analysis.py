import re
import os
import json
import datetime
import geo_ip_lookup

TARGET_DIR = "/tank/peers/json/london"

numerals = re.compile("[0-9]{5,15}")

geo_lookup = geo_ip_lookup.GeoIPDatabase()
all_found_country_codes = []
peer_geo_stats = {}
start = datetime.datetime.now()

for root, dirs, files in os.walk(TARGET_DIR):
    for name in files:
        full_path = os.path.join(root, name)
        match = numerals.search(name)
        timestamp = int(name[match.start():match.end()])
        epoch = datetime.datetime.fromtimestamp(timestamp)
        stream = open(full_path, "r")
        peer_data = json.load(stream)
        stream.close()

        countries = {}
        for peer_connection in peer_data:
            remote_address = peer_connection["network"]["remoteAddress"]
            ip_addr = remote_address.split(":")[0]
            geo_data = geo_lookup.lookup(ip_addr)
            if geo_data == None:
                continue
            country_code = geo_data.country_code
            if country_code not in all_found_country_codes:
                all_found_country_codes.append(country_code)
            if country_code in countries.keys():
                countries[country_code] += 1
            else:
                countries[country_code] = 1

        peer_geo_stats[epoch.isoformat()] = countries

for key in peer_geo_stats.keys():
    country_codes = peer_geo_stats[key].keys()
    for each in all_found_country_codes:
        if each not in country_codes:
            peer_geo_stats[key][each] = 0

csv_filepath = TARGET_DIR + "/country_codes.csv"
csv_file = open(csv_filepath, "w")

index_row = ["Timestamp"]
index_row.extend(all_found_country_codes)

index_row_str = ",".join(index_row) + "\n"
csv_file.write(index_row_str)

for key in peer_geo_stats.keys():
    geo_data = peer_geo_stats[key]
    data_row = [key]
    for each in all_found_country_codes:
        data_row.append(each)
    data_row_str = ",".join(data_row) + "\n"
    csv_file.write(data_row_str)

csv_file.close()

end = datetime.datetime.now()
elapse = end - start
print("Elapsed time: {0}".format_map(elapse))

