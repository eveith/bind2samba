import unittest
import ipaddress
from pathlib import Path

from bind2sambatool import (
    filter_matching_subnet,
    rev4_from_network,
    rev6_from_network,
    add_a,
    add_aaaa,
    add_cname,
    add_mx,
    read_file,
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

    def test_add_a(self):
        r = add_a(
            "foo",
            ipaddress.ip_address("10.17.2.1"),
            "example.com"
        )
        self.assertEqual(
            r,
            [
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    'example.com',
                    'foo',
                    'A',
                    '10.17.2.1'
                ]
            ]
        )
        r = add_a(
            "foo",
            ipaddress.ip_address("10.17.2.1"),
            "example.com",
            [ipaddress.ip_network("10.0.0.0/8")]
        )
        self.assertEqual(
            r,
            [
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    'example.com',
                    'foo',
                    'A',
                    '10.17.2.1'
                ],
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    '10.in-addr.arpa',
                    '1.2.17.10.in-addr.arpa',
                    'PTR',
                    'foo.example.com'
                ]
            ]
        )

    def test_add_aaaa(self):
        r = add_aaaa(
            "foo",
            ipaddress.ip_address("2001:470:76c4:1:2::23"),
            "example.com"
        )
        self.assertEqual(
            r,
            [
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    'example.com',
                    'foo',
                    'AAAA',
                    '2001:470:76c4:1:2::23'
                ]
            ]
        )
        r = add_aaaa(
            "foo",
            ipaddress.ip_address("2001:470:76c4:1:2::23"),
            "example.com",
            [
                ipaddress.ip_network("2001:470:76c4:1::/64"),
                ipaddress.ip_network("2a01:dead:beef::/48"),
                ipaddress.ip_network("2001:470:76c4:1:2::/80")
            ]
        )
        self.assertEqual(
            r,
            [
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    'example.com',
                    'foo',
                    'AAAA',
                    '2001:470:76c4:1:2::23'
                ],
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    '2.0.0.0.1.0.0.0.4.c.6.7.0.7.4.0.1.0.0.2.ip6.arpa',
                    '3.2.0.0.0.0.0.0.0.0.0.0.2.0.0.0.1.0.0.0.4.c.6.7.0.7.4.0.1.0.0.2.ip6.arpa',
                    'PTR',
                    'foo.example.com'
                ]
            ]
        )

    def test_add_cname(self):
        r = add_cname("foo", "bar.baz.com", "example.com")
        self.assertEqual(
            r,
            [
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    'example.com',
                    'foo',
                    'CNAME',
                    'bar.baz.com.example.com'
                ]
            ]
        )

    def test_add_mx(self):
        r = add_mx("DONTCARE", "10 mxserver", "example.com")
        self.assertEqual(
            r,
            [
                [
                    'samba-tool',
                    'dns',
                    'add',
                    'localhost',
                    'example.com',
                    '@',
                    'MX',
                    'mxserver.example.com 10'
                ]
            ]
        )

    def test_read_file(self):
        with open(Path(__file__).parent / "minimal-example.com.db", "r") as f:
            r = read_file(f, None, [], [])
        print(r)


if __name__ == '__main__':
    unittest.main()
