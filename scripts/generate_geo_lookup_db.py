# Generate an sqlite3 database that can be quickly browsed by trie

import MySQLdb

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASS = "thistle2832"
MYSQL_DB = "service"

GET_NETWORK_GEODATA_SQL = """
SELECT
  network,
  locale_code,
  continent_code,
  continent_name,
  country_iso_code,
  country_name
FROM geo_ip_countries
  INNER JOIN geo_ip_locations ON geo_ip_countries.geoname_id = geo_ip_locations.geoname_id;
"""

CREATE_TRIE_TABLE_SQL = """
CREATE TABLE trie (
  parent INTEGER, 
  value INTEGER, 
  country_info_rowid INTEGER
); 
"""

CREATE_COUNTRY_INFO_TABLE_SQL = """
CREATE TABLE country_info(
    local_code CHAR(2),
    continent_code CHAR(2),
    continent_name TEXT,
    country_iso_code CHAR(2),
    country_name TEXT
);
"""

class GeodataSQLite3Database:
    def add_ip(self, ip_address, country_info_rowid):
