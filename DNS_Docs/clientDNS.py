import socket
from socket import *
import struct

DNS_QUERY_TYPES = {
    'A': 1,
    'AAAA': 28
}
class ClientDNS():

    def __init__(self):
        self.client_port = 57217
        self.server_port = 53
        self.ip_add = "10.0.0.123"
        self.dns_server_add = "127.0.0.1"
        self.subnet_mask = None
        self.router = None
        self.ip_result = ""


    def parse_dns_response(self, dns_response, query_data, query_len):
        # Parse the DNS response
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack_from('! H H H H H H', dns_response)
        response_type = struct.unpack_from('! H', dns_response, len(query_data) + 2)[0]
        response_address = ''
        answer_start = 12 + query_len  # Start of answer section
        answer_name, answer_type, answer_class, answer_ttl, answer_rdlen = struct.unpack('! H H H I H', dns_response[
                                                                                                        answer_start: answer_start + 12])
        answer_data = dns_response[answer_start + 12: answer_start + 12 + answer_rdlen]
        if response_type == DNS_QUERY_TYPES['A']:
            response_address = inet_ntoa(answer_data)
        elif response_type == DNS_QUERY_TYPES['AAAA']:
            response_address = socket.inet_ntop(AF_INET6, struct.unpack_from('! 16s', dns_response, len(query_data) + 10)[0])

        self.ip_result = response_address
        print(response_address)

    def send_dns_query(self, hostname, query_type):
        server_address = (self.dns_server_add, self.server_port)
        client_socket = socket(AF_INET, SOCK_DGRAM)
        # Construct the DNS query
        id = 1
        flags = 0x0100  # Standard query with recursion desired
        qdcount = 1
        ancount = 0
        nscount = 0
        arcount = 0
        hostname_labels = hostname.split('.')
        hostname_bytes = b''
        for label in hostname_labels:
            hostname_bytes += struct.pack('! B', len(label)) + label.encode('ascii')
        hostname_bytes += b'\x00'
        query_type = DNS_QUERY_TYPES[query_type]
        query_header = struct.pack('! H H H H H H', id, flags, qdcount, ancount, nscount, arcount)
        query_data = query_header + hostname_bytes + struct.pack('! H H', query_type, 1)
        query_len = len(hostname_bytes + struct.pack('! H H', query_type, 1))

        # Send the DNS query and receive the response
        client_socket.sendto(query_data, server_address)
        response_data, _ = client_socket.recvfrom(1024)
        self.parse_dns_response(response_data, query_data, query_len)

if __name__ == '__main__':
    hostname = "www.google.com"
    query_type = 'A'
    client = ClientDNS()
    client.send_dns_query(hostname, query_type)
