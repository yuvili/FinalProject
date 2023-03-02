# TODO-1: Database (file or a dictionary) - define a TTL for each hostname
# TODO-2: find answer in cache or use os and sys

from scapy.layers.dns import DNSQR, DNS, DNSRR, IP
from scapy.layers.inet import UDP
from scapy.all import *
from socket import *

DNS_IP = "192.168.1.1"

DNS_Question_Record = {}

# Berkeley Packet Filter for sniffing specific DNS packet only
packet_filter = " and ".join([
    "udp dst port 53",  # Filter UDP port 53
    "udp[10] & 0x80 = 0",  # DNS queries only
])


def dns_server(packet):
    # Handle incoming DNS queries
    if DNSQR in packet and packet[DNSQR].qtype == 1:
        print("got a request")
        hostname = packet[DNS].qd[DNSQR].qname
        if hostname in DNS_Question_Record:
            print("found in cache")
            ip_address = DNS_Question_Record[hostname].ip
            hostname_ttl = DNS_Question_Record[hostname].ttl
        else:
            ip_address = gethostbyname(hostname)
            hostname_ttl = 10
            DNS_Question_Record[hostname] = {"ip": ip_address, "ttl": hostname_ttl}

        # Create a DNS response packet with the IP address of the DNS server
        resp_packet = (
                IP(dst=packet[IP].src) /
                UDP(dport=packet[UDP].sport, sport=53) /
                DNS(id=packet[DNS].id, qd=packet[DNS].qd, aa=1, qr=1,
                    an=DNSRR(rrname=packet[DNSQR].qname, ttl=hostname_ttl, rdata=ip_address)))

        send(resp_packet, verbose=False)
        print("sent answer")


def start_server():
    threads = []
    while True:
        try:
            packet = sniff(filter="udp and port 53", count=1)
            packet.summary()
            thread = threading.Thread(target=dns_server, args=packet)
            thread.start()
            threads.append(thread)

        except KeyboardInterrupt:
            print("Shutting down...")
            break

    for thread in threads:  # Wait for all threads to finish
        thread.join()


if __name__ == '__main__':
    start_server()
