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

for root, dirs, files in os.walk(TARGET_DIR):
    for name in files:
        full_path = os.path.join(root, name)
        match = numerals.match(name)
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
            country_code = geo_data.country_code
            if country_code not in all_found_country_codes:
                all_found_country_codes.append(country_code)
            if country_code in countries.keys():
                countries[country_code] += 1
            else:
                countries[country_code] = 1

        peer_geo_stats[epoch.isoformat()] = countries

print(peer_geo_stats)
