import struct
import unittest
from socket import socket
from socket import *

def dns_query(hostname):
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
    query_type = 1
    query_header = struct.pack('! H H H H H H', id, flags, qdcount, ancount, nscount, arcount)
    query_data = query_header + hostname_bytes + struct.pack('! H H', query_type, 1)
    query_len = len(hostname_bytes + struct.pack('! H H', query_type, 1))

    return query_data, query_len

def is_dns_response(dns_response):
    id, flags, qdcount, ancount, nscount, arcount = struct.unpack_from('! H H H H H H', dns_response)
    return flags
def get_dns_response_type(dns_response, query_data):
    id, flags, qdcount, ancount, nscount, arcount = struct.unpack_from('! H H H H H H', dns_response)
    response_type = struct.unpack_from('! H', dns_response, len(query_data) + 2)[0]
    return response_type

def get_dns_response_name(dns_response, query_len):
    query_start = struct.Struct('! H H H H H H').size
    hostname = ''
    while True:
        label_len = dns_response[query_start]
        if label_len == 0:
            break
        hostname += dns_response[query_start + 1: query_start + label_len + 1].decode('ascii') + '.'
        query_start += label_len + 1
    return hostname[0:-1]


def get_dns_response_data(dns_response, query_len, query_packet):
    answer_start = 12 + query_len  # Start of answer section
    answer_name, answer_type, answer_class, answer_ttl, \
        answer_rdlen = struct.unpack('! H H H I H', dns_response[answer_start: answer_start + 12])
    answer_data = dns_response[answer_start + 12: answer_start + 12 + answer_rdlen]
    response_address=''
    if answer_type == 1:
        response_address = inet_ntoa(answer_data)
    elif answer_type == 28:
        response_address = inet_ntop(AF_INET6, struct.unpack_from('! 16s', dns_response, len(query_packet) + 10)[0])

    return response_address

class MyTestCase(unittest.TestCase):
    def test_dns_query(self):
        server_address = ("127.0.0.1", 53)
        client_socket = socket(AF_INET, SOCK_DGRAM)
        query_packet, query_len = dns_query("www.example.com")
        client_socket.sendto(query_packet, server_address)
        response, _ = client_socket.recvfrom(1024)

        # Verify that the response is a valid DNS response
        self.assertEqual(is_dns_response(response), 0x8180)
        self.assertEqual(get_dns_response_type(response, query_packet), 1)
        self.assertEqual(get_dns_response_name(response, query_len), 'www.example.com')
        self.assertIn('93.184.216.34', get_dns_response_data(response, query_len, query_packet))
        client_socket.close()


if __name__ == '__main__':
    unittest.main()
