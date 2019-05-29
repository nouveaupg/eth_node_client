import csv
import re
import unittest

HTTPS_RE = re.compile("^https://.")
DEFAULT_CSV_FILE = "config/ipv4-address-space.csv"


class ClassARDAPServices:
    def __init__(self, config_path: str = None):
        self._rdap_services = {}
        if config_path:
            self._config_path = config_path
        else:
            self._config_path = DEFAULT_CSV_FILE
        with open(self._config_path, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                rdap_uris = row["RDAP"].split("\n")
                if rdap_uris:
                    for line in rdap_uris:
                        if HTTPS_RE.match(line):
                            class_a = int(row["Prefix"].split("/")[0])
                            self._rdap_services[class_a] = line

    def get_rdap_uri(self, ipv4_class_a: int) -> str:
        if ipv4_class_a < 0:
            raise ValueError
        elif ipv4_class_a > 255:
            raise ValueError
        if ipv4_class_a in self._rdap_services:
            return self._rdap_services[ipv4_class_a]
        raise IndexError

    def keys(self) -> list:
        return self._rdap_services.keys()


class TestReserved(unittest.TestCase):
    def setUp(self):
        self._rdap_services = ClassARDAPServices()

    def test_loopback(self):
        with self.assertRaises(IndexError):
            self._rdap_services.get_rdap_uri(127)

    def test_local(self):
        with self.assertRaises(IndexError):
            self._rdap_services.get_rdap_uri(10)


class TestHTTPSEndpoints(unittest.TestCase):
    def setUp(self):
        self._rdap_services = ClassARDAPServices()

    def test_all_endpoints(self):
        for key in self._rdap_services.keys():
            regex_matches = False
            if HTTPS_RE.match(self._rdap_services.get_rdap_uri(key)):
                regex_matches = True
            self.assertTrue(regex_matches)


if __name__ == "__main__":
    unittest.main()
