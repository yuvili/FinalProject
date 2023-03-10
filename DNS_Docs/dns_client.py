from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import UDP, IP
from scapy.sendrecv import sniff, send, sr1, sr, srflood

class ClientDNS():

    def __init__(self):
        self.client_port = 57217
        self.server_port = 53
        self.ip_add = "10.0.0.123"
        self.dns_server_add = "10.0.0.1"
        self.subnet_mask = None
        self.router = None
        self.ip_result = ""

    def parse_dns_response(self, packet):
        self.ip_result = packet[DNS].an[DNSRR].rdata
        print(self.ip_result)

    def is_response(self, dns_packet):
        print("found a responce")
        if DNS in dns_packet and dns_packet[DNS].qr == 1:
            self.parse_dns_response(dns_packet)

    def send_dns_query(self, hostname):
        # Build a DNS query packet
        packet = (
                IP(src=self.ip_add, dst=self.dns_server_add) /
                UDP(sport=self.client_port, dport=self.server_port) /
                DNS(rd=1, qr=0, qd=DNSQR(qname=hostname, qtype=1))
        )
        responce = srflood(packet, filter=f'udp and port 53', verbose=False, count=1, prn=self.is_response)
        self.is_response(responce)
        # sniff(filter=f'udp and port 53', prn=self.is_response, count=1)

if __name__ == '__main__':
    hostname = "www.google.com"
    client = ClientDNS()
    client.send_dns_query(hostname)
