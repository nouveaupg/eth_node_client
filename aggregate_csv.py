import csv
import re
import os
import datetime

numeral = re.compile("[0-9]{9,12}")

all_country_codes = []

CITY = "london"

country_data = {}
for root, dirs, files in os.walk("/home/jack/{0}_csv".format(CITY)):
    for name in files:
        match = numeral.search(name)
        timestamp = int(name[match.start():match.end()])
        dt = datetime.datetime.fromtimestamp(timestamp)
        input_name = os.path.join(root, name)
        print("Processing: {0}".format(input_names))
        with open(input_name) as f:
            reader = csv.reader(f)
            peer_data = {}
            for row in reader:
                if row[0] not in all_country_codes:
                    all_country_codes.append(row[0])
                peer_data[row[0]] = int(row[1])
            country_data[dt.isoformat()] = peer_data

output_data = []
for key in country_data.keys():
    peer_data = country_data[key]
    peer_countries = peer_data.keys()
    # put in zero values for unrepresented countries
    for each_country in all_country_codes:
        if each_country not in peer_countries:
            peer_countries[each_country] = 0
    new_dict = dict(peer_data)
    new_dict["Timestamp"] = key
    output_data.append(new_dict)


all_country_codes.insert(0, "Timestamp")

with open("{0}_aggregate.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, all_country_codes, quoting=csv.QUOTE_NONE)
    writer.writeheader()
    writer.writerows(output_data)

