# TODO-1: Database (file or a dictionary) - define a TTL for each hostname
# TODO-2: find answer in cache or use os and sys

from scapy.layers.dns import DNSQR, DNS, DNSRR
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import *
from socket import *
import threading


DNS_IP = "10.0.0.1"

DNS_Cache = {}

# Berkeley Packet Filter for sniffing specific DNS packet only
packet_filter = " and ".join([
    "udp dst port 53",  # Filter UDP port 53
    "udp[10] & 0x80 = 0",  # DNS queries only
])


def dns_server(packet):
    # Handle incoming DNS queries
    if DNSQR in packet and packet[DNSQR].qtype == 1:
        print("got a request")
        hostname = packet[DNS].qd[DNSQR].qname.decode('utf-8')
        hostname = hostname[0:-1]
        print("from server hostname: "+hostname)

        if len(DNS_Cache) != 0 and hostname in DNS_Cache:
            print("found in cache")
            ip_address = DNS_Cache[hostname]["ip"]
            hostname_ttl = DNS_Cache[hostname]["ttl"]

        else:
            ip_address = gethostbyname(hostname)
            hostname_ttl = 10
            DNS_Cache[hostname] = {"ip": ip_address, "ttl": hostname_ttl}

        # Create a DNS response packet with the IP address of the DNS server
        resp_packet = (
                IP(dst=packet[IP].src) /
                UDP(dport=packet[UDP].sport, sport=53) /
                DNS(id=packet[DNS].id, qd=packet[DNS].qd, aa=1, qr=1,
                    an=DNSRR(rrname=packet[DNSQR].qname, ttl=hostname_ttl, rdata=ip_address)))

        print(packet[UDP].sport)
        send(resp_packet, verbose=False)
        print("sent answer")

def start_server():
    while True:
        try:
            sniff(filter="udp and port 53",prn=dns_server, count=1)
        except KeyboardInterrupt:
            print("Shutting down...")
            break


if __name__ == '__main__':
    start_server()
