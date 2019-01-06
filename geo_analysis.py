import json
import geo_ip_lookup
import time
import sys
import os


def analyze_data(input_name,geo_lookup):
    start = time.time()
    stream = open(input_name, "r")
    peer_data = json.load(stream)
    stream.close()

    countries = {}
    total = len(peer_data)
    ctr = 0
    print("GeoIP lookup of {0} peer connections...".format(total))
    for peer_connection in peer_data:
        remote_address = peer_connection["network"]["remoteAddress"]
        ip_addr = remote_address.split(":")[0]
        geo_data = geo_lookup.lookup(ip_addr)
        ctr += 1
        if ctr % 20 == 0:
            print("{0:.0f}% percent complete".format((ctr / total) * 100.0))
        if geo_data is None:
            continue
        country_code = geo_data.country_code
        if country_code in countries.keys():
            countries[country_code] += 1
        else:
            countries[country_code] = 1
    end = time.time()
    print("Elapsed time: {0:.2f} seconds".format(end-start))
    print("Average lookup time: {0:.2f} seconds".format(geo_lookup.avg_lookup_time))
    output_name = "/home/jack/" + input_name.split(".")[0] + ".csv"
    stream = open(output_name, "w")
    for key in countries.keys():
        stream.write("{0},{1}\n".format(key, countries[key]))
    stream.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python geo_analysis.py peers_<timestamp>.json")
        sys.exit(1)
    geo_lookup = geo_ip_lookup.GeoIPDatabase()
    input_name = sys.argv[1]
    for root, dirs, files in os.walk("/tank/peers/json/amsterdam"):
        for name in files:
            input_name = os.path.join(root, name)
            analyze_data(input_name, geo_lookup)

