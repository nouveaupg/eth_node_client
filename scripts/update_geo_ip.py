import MySQLdb

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = "beligerent8136"
MYSQL_DB = "geo_ip"

db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)

cursor = db.cursor()
# cursor.execute("SELECT geoname_id, continent_name,country_name FROM geo_ip_locations")
#
# for row in cursor:
#     continent_name = row[1].replace('\"', "")
#     if row[2]:
#         country_name = row[2].replace('\"', "")
#     update_cursor = db.cursor()
#     sql = "UPDATE geo_ip_locations SET continent_name=%s,country_name=%s WHERE geoname_id=%s"
#     update_cursor.execute(sql, (continent_name,
#                                 country_name,
#                                 row[0]))
#     db.commit()

cursor.execute("SELECT COUNT(*) FROM geo_ip_countries")
country_count = cursor.fetchone()
cursor.execute("SELECT serial,network FROM geo_ip_countries")
ctr = 0
for c in cursor:
    network = c[1]
    parts = network.split(".")
    network_ab = "{0}.{1}".format(parts[0], parts[1])
    inner_cursor = db.cursor()
    sql = "UPDATE geo_ip_countries SET network_class_ab=%s WHERE geoname_id=%s"
    inner_cursor.execute(sql, (network_ab, c[0]))
    ctr += 1
    if ctr % 1000 == 0:
        db.commit()
        print("{0:2f}%".format(ctr/country_count[0]))
