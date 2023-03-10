import threading
import unittest
from scapy.layers.dns import DNSQR, DNS, DNSRR
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import *
from DNS_Docs import ServerDNS as dns_server


def dns_query(hostname):
    # Build a DNS query packet
    packet = (
            IP(dst="10.0.0.1") /
            UDP(dport=53) /
            DNS(rd=1, qr=0, qd=DNSQR(qname=hostname, qtype=1))
    )
    return packet
class MyTestCase(unittest.TestCase):
    # def test_something(self):
    #     self.assertEqual(True, False)  # add assertion here

    def test_dns_query(self):
        # Send DNS query message to server
        packet = IP(dst='127.0.0.1') / UDP(dport=53, sport=1234) / DNS(id=1, qr=0,
                                                                      qd=DNSQR(qname='www.example.com', qtype='A'))
        send(packet)
        dns_server.start_server()
        response_packet = sniff(filter="udp and port 1234", count=1)
        self.assertIsNotNone(response_packet)
        print(response_packet[0])
        # self.assertTrue(response_packet.haslayer(DNS))
        # self.assertEqual(response_packet[DNS].id, packet[DNS].id)
        # self.assertEqual(response_packet[DNS].qr, 1)
        # self.assertEqual(response_packet[DNS].an.rrname, packet[DNSQR].qname)


if __name__ == '__main__':
    unittest.main()
