from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import UDP, IP
from scapy.sendrecv import sniff, send
from DHCP_Docs.dhcp_client import ClientDHCP


class ClientDNS():

    def __init__(self,clientdhcp:ClientDHCP=None):
        self.client_port = 57217
        self.server_port = 53
        self.ip_add = None
        self.dns_server_add = None
        self.subnet_mask = None
        self.router = None

        if clientdhcp is not None:
            self.ip_add = clientdhcp.ip_add
            self.dns_server_add = clientdhcp.dns_server_add
            self.subnet_mask = clientdhcp.subnet_mask
            self.router = clientdhcp.router

    def is_response(self, dns_packet):
        print("found a responce")
        if DNS in dns_packet and dns_packet[DNS].qr == 1:
            self.parse_dns_response(dns_packet)

    def send_dns_query(self, hostname):
        print(self.ip_add)
        # Build a DNS query packet
        packet = (
                IP(src=self.ip_add, dst=self.dns_server_add) /
                UDP(sport=self.client_port, dport=self.server_port) /
                DNS(rd=1, qr=0, qd=DNSQR(qname=hostname, qtype=1))
        )
        send(packet)
        sniff(filter=f'udp and port 53', prn=self.is_response, verbose=False)

    def parse_dns_response(self, packet):
        answer = packet[DNS].an[DNSRR].rdata
        print(answer)


if __name__ == '__main__':
    hostname = "www.google.com"
    client = ClientDNS()
    client.send_dns_query(hostname)
