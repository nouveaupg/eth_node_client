import ipaddress
import MySQLdb
import time
import sys

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = "thistle2832"
MYSQL_DB = "service"


class GeoLocatedIP:
    def __init__(self,
                 ip_address,
                 country_code,
                 country_name,
                 continent,
                 eu_member=False,
                 satellite_provider=False,
                 anonymous_proxy=False):
        self.ip_address = ip_address
        self.country_code = country_code
        self.country_name = country_name
        self.continent = continent
        if anonymous_proxy > 0:
            self.anonymous_proxy = True
        else:
            self.anonymous_proxy = False
        if satellite_provider > 0:
            self.satellite_provider = True
        else:
            self.satellite_provider = False
        if eu_member > 0:
            self.eu_member = True
        else:
            self.eu_member = False

    def __str__(self):
        return str(self.ip_address) + "({0})".format(self.country_name)


class GeoIPDatabase:
    def __init__(self):
        self.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
        self.lookup_counter = 0
        self.success_counter = 0
        self.failure_counter = 0
        self.avg_lookup_time = 0

    def update_failures(self, start, end):
        elapsed = end - start
        self.failure_counter += 1
        aggregate_lookup_time = self.avg_lookup_time * self.lookup_counter
        self.lookup_counter += 1
        aggregate_lookup_time += elapsed
        self.avg_lookup_time = aggregate_lookup_time / self.lookup_counter

    def update_success(self, start, end):
        elapsed = end - start
        self.success_counter += 1
        aggregate_lookup_time = self.avg_lookup_time * self.lookup_counter
        self.lookup_counter += 1
        aggregate_lookup_time += elapsed
        self.avg_lookup_time = aggregate_lookup_time / self.lookup_counter

    def lookup(self, ipv4_address_string):
        parts = ipv4_address_string.split(".")
        match_exp = parts[0] + "." + parts[1]
        sql = "SELECT network, geoname_id FROM geo_ip_countries WHERE network_class_ab=%s"
        ip_address = ipaddress.IPv4Address(ipv4_address_string)
        start = time.time()
        c = self.db.cursor()
        c.execute(sql, (match_exp,))
        for row in c:
            network = ipaddress.IPv4Network(row[0])
            if ip_address in network:
                sql = "SELECT country_iso_code,country_name,continent_name,eu_member FROM geo_ip_locations"
                sql += " WHERE geoname_id=%s"
                c.execute(sql, (row[1],))
                inner_row = c.fetchone()
                if inner_row:
                    end = time.time()
                    self.update_success(start, end)
                    return GeoLocatedIP(ip_address,
                                        inner_row[0],
                                        inner_row[1],
                                        inner_row[2],
                                        inner_row[3])

        end = time.time()
        self.update_failures(start, end)
        return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db = GeoIPDatabase()
        geo_data = db.lookup(sys.argv[1])
        if geo_data:
            print(geo_data)
        else:
            print("GeoIP lookup failed for: {0}".format(sys.argv[1]))
