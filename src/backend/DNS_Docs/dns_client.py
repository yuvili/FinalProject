import socket
import random
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
        self.ip_address = ""
        self.dns_server_add = ""
        self.subnet_mask = None
        self.router = None
        self.ip_result = ""

    def parse_dns_response(self, dns_response, query_data, query_len):
        """
        When given a DNS response, this function is used to extract the requested IP address
        :param dns_response: server's response
        :param query_data: client's originally query
        :param query_len: client's originally query length
        """

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

    def send_dns_query(self, hostname, query_type):
        """
        Sending a DNS query when given a hostname and query type.
        :param hostname: a hostname to find it's ip
        :param query_type: type of dns query
        """
        server_address = (self.dns_server_add, self.server_port)
        client_socket = socket(AF_INET, SOCK_DGRAM)
        # Construct the DNS query
        id = random.randint(1, 2 ** 16 - 1)
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
        print("---------------------")
        print("DNS Client sent query")
        response_data, _ = client_socket.recvfrom(1024)
        print("---------------------")
        print("DNS Client got response")
        self.parse_dns_response(response_data, query_data, query_len)

if __name__ == '__main__':
    hostname = "www.google.com"
    query_type = 'A'
    client = ClientDNS()
    client.send_dns_query(hostname, query_type)
