import unittest
import ipaddress

from bind2sambatool import (
    filter_matching_subnet,
    rev4_from_network,
    rev6_from_network,
)

class Bind2SambaToolTest(unittest.TestCase):
    def test_filter_matching_subnet_ipv4(self):
        net1 = ipaddress.ip_network("10.0.1.0/24")
        net2 = ipaddress.ip_network("172.19.0.0/16")
        net3 = ipaddress.ip_network("172.19.5.0/24")
        net4 = ipaddress.ip_network("172.19.1.0/24")
        x = filter_matching_subnet(
            ipaddress.ip_address("172.19.5.1"),
            [ net1, net2, net3, net4]
        )
        self.assertEqual(x, net3)
        x = filter_matching_subnet(
            ipaddress.ip_address("192.168.5.1"),
            [ net1, net2, net3, net4]
        )
        self.assertIsNone(x)

    def test_filter_matching_subnet_ipv6(self):
        net1 = ipaddress.ip_network("2001:aa0:7020::/48")
        net2 = ipaddress.ip_network("2001:470:76c4::/48")
        net3 = ipaddress.ip_network("2001:470:76c4:1::/64")
        net4 = ipaddress.ip_network("2001:470:76c4:2::/64")
        x = filter_matching_subnet(
                ipaddress.ip_address("2001:0470:76c4:1::2"),
            [ net1, net2, net3, net4]
        )
        self.assertEqual(x, net3)
        x = filter_matching_subnet(
                ipaddress.ip_address("2a01:4f8:191:7396::2"),
            [ net1, net2, net3, net4]
        )
        self.assertIsNone(x)

    def test_rev4_from_network(self):
        self.assertEqual(
            "168.192.in-addr.arpa",
            rev4_from_network(ipaddress.ip_network("192.168.0.0/16"))
        )
        self.assertEqual(
            "16.172.in-addr.arpa",
            rev4_from_network(ipaddress.ip_network("172.16.0.0/14"))
        )

    def test_rev6_from_network(self):
        self.assertEqual(
            "1.0.0.0.4.c.6.7.0.7.4.0.1.0.0.2.ip6.arpa",
            rev6_from_network(ipaddress.ip_network("2001:470:76c4:1::/64"))
        )


if __name__ == '__main__':
    unittest.main()
