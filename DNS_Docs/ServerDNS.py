# TODO-1: Database (file or a dictionary) - define a TTL for each hostname
# TODO-2: find answer in cache or use os and sys

import socket
import struct
from socket import *

# Define the DNS header format
DNS_HEADER_FORMAT = struct.Struct('! H H H H H H')

# Define a dictionary of DNS query types
DNS_QUERY_TYPES = {
    'A': 1,     # IPv4 address
    'AAAA': 28, # IPv6 address
    'MX': 15,   # Mail exchange
    'CNAME': 5, # Canonical name
}

DNS_IP = "10.0.0.1"

DNS_Cache = {}


def handle_dns_query(data, client_address, server_socket):
    # Parse the DNS header
    id, flags, qdcount, ancount, nscount, arcount = DNS_HEADER_FORMAT.unpack_from(data)

    # Check if this is a DNS query (i.e., QR bit is 0)
    if flags & 0x8000 == 0:
        # Extract the DNS query name and type
        query_start = DNS_HEADER_FORMAT.size
        hostname = ''
        while True:
            label_len = data[query_start]
            if label_len == 0:
                break
            hostname += data[query_start + 1: query_start + label_len + 1].decode('ascii') + '.'
            query_start += label_len + 1
        query_type = struct.unpack_from('! H', data, query_start + 1)[0]
        hostname = hostname[0:-1]
        ip_address = ''
        print(hostname)
        if len(DNS_Cache) != 0 and hostname in DNS_Cache:
            print("found in cache")
            ip_address = DNS_Cache[hostname]["ip"]
            hostname_ttl = DNS_Cache[hostname]["ttl"]
        else:
            ip_address = gethostbyname(hostname)
            hostname_ttl = 10
            DNS_Cache[hostname] = {"ip": ip_address, "ttl": hostname_ttl}

        # # Determine the IP address to return based on the query name and type
        # ip_address = '127.0.0.1'  # Default to localhost
        # if query_name == 'example.com' and query_type == DNS_QUERY_TYPES['A']:
        #     ip_address = '192.0.2.1'  # Example IPv4 address
        # elif query_name == 'example.com' and query_type == DNS_QUERY_TYPES['AAAA']:
        #     ip_address = '2001:db8::1'  # Example IPv6 address

        hostname_labels = hostname.split('.')
        hostname_bytes = b''
        for label in hostname_labels:
            hostname_bytes += struct.pack('! B', len(label)) + label.encode('ascii')
        hostname_bytes += b'\x00'

        flags = 0x8180 # Set QR bit to 1
        qdcount = 1
        ancount = 1
        nscount = 0
        arcount = 0

        # Construct the DNS response
        response_header = struct.pack('! H H H H H H', id, flags, qdcount, ancount, nscount, arcount)
        response_query = hostname_bytes  + struct.pack('! H H', query_type, 1) # Only copy QNAME and QTYPE
        response_answer = struct.pack('! H H H I H', 0xC00C, query_type, 1, 300, 4) + inet_pton(AF_INET, ip_address)
        response_data = response_header + response_query + response_answer

        # Send the DNS response
        server_socket.sendto(response_data, client_address)

def start_server():
    # Create a UDP socket to listen for DNS queries
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 53))

    print('DNS server listening on port 53...')
    while True:
        data, client_address = server_socket.recvfrom(1024)
        handle_dns_query(data, client_address, server_socket)


if __name__ == '__main__':
    start_server()