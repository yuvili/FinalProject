import binascii
import struct
import unittest
import socket
from socket import *
import threading
import random

from DHCP_Docs import dhcp_server

def build_dhcp_request_packet(server_id, offered_addr):
    op_code = 1
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    xid = 11132
    secs = 0
    flags = 0x0000
    ciaddr = "0.0.0.0"
    yiaddr = "0.0.0.0"
    siaddr = "0.0.0.0"
    giaddr = "0.0.0.0"
    chaddr = "b0:be:83:1e:0a:30"
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

    mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
    request_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                     inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                     inet_pton(AF_INET, giaddr) + mac_address_bytes + \
                     padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x03'  # DHCP message type: 3 = DHCP Request
    server_id = b'\x36\x04' + inet_pton(AF_INET,server_id)
    request_addr = b'\x32\x04' + offered_addr
    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + server_id + request_addr + end

    # Build the full packet
    packet = request_header + dhcp_options

    return packet

def parse_dhcp_packet_options(packet):
    print("in parce")
    print(packet[240:])
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', packet[0:34])
    options = {
        "op_code": op_code,
        "htype": htype,
        "hlen": hlen,
        "hops": hops,
        "xid": xid,
        "secs": secs,
        "flags": flags,
        "ciaddr": ciaddr,
        "your_address": yiaddr,
        "siaddr": siaddr,
        "giaddr":giaddr,
        "chaddr": chaddr,
        "message_type": packet[240:243],
        "server_id": inet_ntoa(struct.unpack("! 4s", packet[245: 249])[0]),
        "lease_time": struct.unpack("! I", packet[251: 255])[0],
        "renew_val_time": struct.unpack("! I", packet[257: 261])[0],
        "rebinding_time": struct.unpack("! I", packet[262: 266])[0],
        "subnet_mask": struct.unpack("! 4s", packet[269: 273])[0],
        "broadcast_address": struct.unpack("! 4s", packet[275: 279])[0],
        "router":struct.unpack("! 4s", packet[281: 285])[0],
        "dns_server": struct.unpack("! 4s", packet[287: 291])[0]
    }
    print(options)
    # message_type = struct.unpack("! H", options_data[244])[0]
    # server_id = struct.unpack("! 4s", options_data[245: 249])[0]
    # lease_time = struct.unpack("! I", options_data[251: 255])[0]
    # renew_val_time = struct.unpack("! I", options_data[257: 261])[0]
    # rebinding_time = struct.unpack("! I", options_data[262: 266])[0]
    # subnet_mask = struct.unpack("! 4s", options_data[269: 273])[0]
    # broadcast_address = struct.unpack("! 4s", options_data[275: 279])[0]
    # router = struct.unpack("! 4s", options_data[281: 285])[0]
    # dns_server = struct.unpack("! 4s", options_data[287: 291])[0]

    return options
def client_discover(client_socket):
    transaction_id = random.randint(1, 2 ** 32 - 1)
    server_address = ("255.255.255.255", 67)

    op_code = 1
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    xid = transaction_id
    secs = 0
    flags = 0x0000
    ciaddr = "0.0.0.0"
    yiaddr = "0.0.0.0"
    siaddr = "0.0.0.0"
    giaddr = "0.0.0.0"
    chaddr = "b0:be:83:1e:0a:30"
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

    mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
    discover_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                      inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                      inet_pton(AF_INET, giaddr) + mac_address_bytes + \
                      padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x01'  # DHCP message type: 1 = DHCP DISCOVER
    client_id = b'\x3d\x06' + mac_address_bytes  # DHCP client identifier: 6 bytes for MAC address
    request_list = b'\x37\x03\x03\x01\x06'  # DHCP parameter request list: requested options are subnet mask, router, DNS server
    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + client_id + request_list + end

    packet = discover_header + dhcp_options
    client_socket.sendto(packet, server_address)
class MyTestCase(unittest.TestCase):

    def test_dhcp_discover(self):
        thread = threading.Thread(target=dhcp_server.start_server)
        thread.start()
        # Send a DHCP discover packet
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(("0.0.0.0", 68))
        client_discover(client_socket)
        print("after discover")

        # Wait for a DHCP offer packet
        client_socket.settimeout(5.0)
        try:
            dhcp_server.stop_server()
            offer_packet = client_socket.recv(2048)
        except socket.timeout:
            self.fail("Did not receive a DHCP offer packet")

        print("recieved packet")
        client_socket.close()
        thread.join()

        # Parse the offer packet and check the response fields
        offer_options = parse_dhcp_packet_options(offer_packet)
        print("after parce")
        self.assertTrue(offer_options['message_type'] == b'5\x01\x02')
        self.assertTrue(offer_options['server_id'] == "10.0.0.1")
        print("done test disover")

    def test_dhcp_request(self):
        thread = threading.Thread(target=dhcp_server.start_server)
        thread.start()
        # Send a DHCP request packet
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(("0.0.0.0", 68))

        client_discover(client_socket)

        offer_packet = client_socket.recv(2048)
        offer_options = parse_dhcp_packet_options(offer_packet)

        packet = build_dhcp_request_packet(offer_options['server_id'], offer_options['your_address'])
        client_socket.sendto(packet, ("255.255.255.255", 67))

        # Wait for a DHCP ACK packet
        client_socket.settimeout(5.0)
        try:
            dhcp_server.stop_server()
            ack_packet = client_socket.recv(2048)
        except socket.timeout:
            self.fail("Did not receive a DHCP ACK packet")

        client_socket.close()
        thread.join()

        # Parse the ACK packet and check the response fields
        ack_options = parse_dhcp_packet_options(ack_packet)
        self.assertTrue(ack_options['message_type'] == b'5\x01\x05')
        self.assertTrue(ack_options['server_id'] == "10.0.0.1")
        self.assertTrue(ack_options['your_address'] == offer_options['your_address'])


if __name__ == '__main__':
    unittest.main()
