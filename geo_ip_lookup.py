from json import JSONDecodeError
from ipaddress import IPv4Address
import ipaddress
import MySQLdb
import time
import sys
import json

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = "thistle2832"
MYSQL_DB = "service"


class GeoIPLookupException(Exception):
    """ Error retrieving geolocation for IP """
    pass


class GeoIPLookupNotFound(GeoIPLookupException):
    """ Geolocation not found for IP """
    pass


class GeoIPLookupInvalidData(GeoIPLookupException):
    """ Invalid data """
    pass


class GeoLocatedIP:
    def __init__(self,
                 ip_address: IPv4Address,
                 country_code: str,
                 country_name: str,
                 continent: str,
                 eu_member: bool = False,
                 satellite_provider: bool = False,
                 anonymous_proxy: bool = False):
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

    def serialize_json(self) -> str:
        output = {
            "ipv4_address": str(self.ip_address),
            "country_code": self.country_code,
            "country_name": self.country_name,
            "continent": self.continent,
            "anonymous_proxy": self.anonymous_proxy,
            "satellite_provider": self.satellite_provider,
            "eu_member": self.eu_member
        }
        return json.dumps(output)

    def __str__(self) -> str:
        return str(self.ip_address) + "({0})".format(self.country_name)


class GeoIPDatabase:
    def __init__(self, db=None):
        if db:
            self.db = db
        else:
            self.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
        self.lookup_counter = 0
        self.success_counter = 0
        self.failure_counter = 0
        self.avg_lookup_time = 0

    @staticmethod
    def deserialize_json(json_data: str) -> GeoLocatedIP:
        try:
            data = json.loads(json_data)
            ip_address = None
            country_code = None
            country_name = None
            continent = None
            satellite_provider = None
            eu_member = None
            anonymous_proxy = None
            if "ipv4_address" in data:
                ip_address = IPv4Address(data["ipv4_address"])
            if "country_code" in data:
                country_code = data["country_code"]
            if "country_name" in data:
                country_name = data["country_name"]
            if "continent" in data:
                continent = data["continent"]
            if "satellite_provider" in data:
                satellite_provider = data["satellite_provider"]
            if "eu_member" in data:
                eu_member = data["eu_member"]
            if "anonymous_proxy" in data:
                anonymous_proxy = data["anonymous_proxy"]
            new_object = GeoLocatedIP(ip_address, country_code, country_name, continent,
                                      eu_member, satellite_provider, anonymous_proxy)
            return new_object
        except JSONDecodeError:
            raise GeoIPLookupInvalidData

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
        start = time.perf_counter()
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
                    end = time.perf_counter()
                    self.update_success(start, end)
                    return GeoLocatedIP(ip_address,
                                        inner_row[0],
                                        inner_row[1],
                                        inner_row[2],
                                        inner_row[3])

        end = time.perf_counter()
        self.update_failures(start, end)
        raise GeoIPLookupNotFound


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db = GeoIPDatabase()
        try:
            geo_data = db.lookup(sys.argv[1])
            if geo_data:
                print(geo_data)
        except GeoIPLookupNotFound:
            print("GeoIP lookup failed for: {0}".format(sys.argv[1]))
