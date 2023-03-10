# Scope - how many IP addresses are available
# Database to store IP, Mac add, Device name
# Lease time - Thread that always checks TTL for the IP address
import binascii
import struct
import threading
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import *
from scapy.utils import mac2str
import random
import socket
from socket import *

# DHCP message types
MSG_TYPE_DISCOVER = 1
MSG_TYPE_OFFER = 2
MSG_TYPE_REQUEST = 3
MSG_TYPE_DECLINE = 4
MSG_TYPE_ACK = 5
MSG_TYPE_NAK = 6
MSG_TYPE_RELEASE = 7
MSG_TYPE_INFORM = 8

# DHCP operation codes
OP_REQUEST = 1
OP_REPLY = 2

SERVER_IP = "10.0.0.1"
DNS_SERVER_IP = '127.0.0.1'
SERVER_PORT = 67
CLIENT_PORT = 68
SCOPE = 254
LEASE = 86400
BROADCAST_IP = "255.255.255.255"
available_addresses = []
log_file = {}


def generate_ip_addresses():
    # Generate a random IP address in the range 10.0.0.2 to 10.0.0.254
    for i in range(2, SCOPE):
        available_addresses.append(f"10.0.0.{str(i)}")


# def offer(packet):
#     print("start offer")
#     # dhcp_header = struct.unpack('! B B B B I H H 4s4s4s4s', packet[0:28])
#     #
#     # # Print the fields in the DHCP header
#     # print('Opcode: ', dhcp_header[0])
#     # print('Hardware type: ', dhcp_header[1])
#     # print('Hardware address length: ', dhcp_header[2])
#     # print('Hop count: ', dhcp_header[3])
#     # print('Transaction ID: ', dhcp_header[4])
#     # print('Seconds elapsed: ', dhcp_header[5])
#     # print('Flags: ', dhcp_header[6])
#     # print('Client IP address: ', inet_ntoa(dhcp_header[7]))
#     # print('Your IP address: ', inet_ntoa(dhcp_header[8]))
#     # print('Server IP address: ', inet_ntoa(dhcp_header[9]))
#     # print('Gateway IP address: ', inet_ntoa(dhcp_header[10]))
#     # Define the callback function for sniffing DHCP Discover packets
#
#     # client_mac = struct.unpack('!6s6s', packet[6:6 + 12])[0]
#     # print(client_mac)
#     op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack('! B B B B I H H 4s4s4s4s16s', packet[0:28+16])
#
#     offered_ip = random.choice(available_addresses)
#     op_code = MSG_TYPE_OFFER
#     htype = 1  # Ethernet
#     hlen = 6  # Address length
#     hops = 0
#     xid = xid
#     secs = 0
#     flags = 0x0000
#     ciaddr = ciaddr
#     yiaddr = inet_pton(AF_INET, offered_ip)
#     siaddr = inet_pton(AF_INET, SERVER_IP)
#     giaddr = inet_pton(AF_INET, "0.0.0.0")
#     # chaddr = packet[12]
#     padding = b'\x00' * 10  # padding (unused)
#     sname = b'\x00' * 64  # srchostname
#     file = b'\x00' * 128  # bootfilename
#     magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99
#
#     discover_header = struct.pack('! B B B B I H H 4s4s4s4s', op_code, htype, hlen, hops, xid, secs, flags,
#                                   ciaddr, yiaddr,siaddr, giaddr) + chaddr + padding + sname + file + magic_cookie
#
#     msg_type = b'\x35\x01\x01'  # DHCP message type: 1 = DHCP DISCOVER
#     # par_req_list = b'\x37\x0d\x01\x1c\x02\x03\x0f\x06\x77\x0c\x2c\x2f\x1a\x79\x2a'
#     client_id = b'\x3d\x06' + chaddr  # DHCP client identifier: 6 bytes for MAC address
#     end = b'\xff'  # end of options marker
#     dhcp_options = msg_type + client_id + end
#
#     # Construct the DHCP Offer packet
#     dhcp_offer = b'\x02\x01\x06\x00' + \
#                  b'\x39\x03\x00\x00\x01\x00\x00\x00' + \
#                  b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
#                  packet[16:20] + \
#                  b'\xff\xff\xff\x00' + \
#                  b'\x03\x02\x04\xff\xff\xff\x00' + \
#                  b'\x06\x0c\x2b\x06\x01\x05\x2b\x0f\x03\x06\x2b\x0e\x03\x0f\x01\x00\x06\x0f\x02\x01'
#
#     dhcp_offer = discover_header + dhcp_options
#     # Create a socket object and set the socket options
#     server_socket = socket(AF_INET, SOCK_DGRAM)
#     # server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#     server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#     server_socket.bind((SERVER_IP, 67))
#
#     # Set the destination address and port
#     dest_addr = ('255.255.255.255', 68)
#
#     # Send the DHCP Offer packet to the client
#     server_socket.sendto(dhcp_offer, dest_addr)
#
#     # Close the socket
#     server_socket.close()
#
#     print("done offer")

def offer(packet):
    print("start offer")
    # if packet[IP].src != "0.0.0.0":
    #     return
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack('! B B B B I H H 4s4s4s4s6s', packet[0:28+6])

    print('Opcode: ', op_code)
    print('Hardware type: ', htype)
    print('Hardware address length: ', hlen)
    print('Hop count: ', hops)
    print('Transaction ID: ', xid)
    print('Seconds elapsed: ', secs)
    print('Flags: ', flags)
    print('Client IP address: ', inet_ntoa(ciaddr))
    print('Your IP address: ', inet_ntoa(yiaddr))
    print('Server IP address: ', inet_ntoa(siaddr))
    print('Gateway IP address: ', inet_ntoa(giaddr))
    print('Mac address: ', chaddr)
    print(type(chaddr))

    mac_string = binascii.hexlify(chaddr).decode('utf-8')
    client_mac_add = ':'.join(mac_string[i:i + 2] for i in range(0, len(mac_string), 2))

    offered_ip = random.choice(available_addresses)
    transaction_id = xid
    offer_packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
            IP(src=SERVER_IP, dst=offered_ip) /
            UDP(sport=SERVER_PORT, dport=CLIENT_PORT) /
            BOOTP(
                op=OP_REPLY,
                yiaddr=offered_ip,
                siaddr=SERVER_IP,
                chaddr=mac2str(client_mac_add),
                xid=transaction_id,
            ) /
            DHCP(options=[
                ("message-type", MSG_TYPE_OFFER),
                ("server_id", SERVER_IP),
                ("lease_time", LEASE),
                ("subnet_mask", "255.255.255.0"),
                ("router", "10.0.0.1"),
                ("name_server", DNS_SERVER_IP),
                ("domain", "localdomain"),
                "end"]
            )
    )
    sendp(offer_packet, verbose=False)
    print("done offer")

# def ack(packet):
#     client_mac_add = packet[Ether].src
#     transaction_id = packet[BOOTP].xid
#     chosen_ip = packet[DHCP].options[2][1]
#
#     if chosen_ip not in available_addresses:
#         print("chosen address not available")
#         nak(packet)
#         return
#
#     info = {
#         "MAC address": client_mac_add,
#         "Lease time": LEASE
#     }
#
#     log_file[chosen_ip] = info
#     available_addresses.remove(chosen_ip)
#
#     ack_packet = (
#             Ether(dst="ff:ff:ff:ff:ff:ff", type=0x800) /
#             IP(src=SERVER_IP, dst=BROADCAST_IP) /
#             UDP(sport=SERVER_PORT, dport=CLIENT_PORT) /
#             BOOTP(
#                 op=OP_REPLY,
#                 yiaddr=chosen_ip,
#                 siaddr=SERVER_IP,
#                 chaddr=mac2str(client_mac_add),
#                 xid=transaction_id,
#             ) /
#             DHCP(options=[
#                 ("message-type", MSG_TYPE_ACK),
#                 ("server_id", SERVER_IP),
#                 ("lease_time", LEASE),
#                 ("broadcast_address", "127.0.0.255"),
#                 ("router", "10.0.0.1"),
#                 ("name_server", DNS_SERVER_IP),
#                 "end"]
#             )
#     )
#     sendp(ack_packet, verbose=False)

def ack(packet):
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', packet[0:28 + 6])

    print('Opcode: ', op_code)
    print('Hardware type: ', htype)
    print('Hardware address length: ', hlen)
    print('Hop count: ', hops)
    print('Transaction ID: ', xid)
    print('Seconds elapsed: ', secs)
    print('Flags: ', flags)
    print('Client IP address: ', inet_ntoa(ciaddr))
    print('Your IP address: ', inet_ntoa(yiaddr))
    print('Server IP address: ', inet_ntoa(siaddr))
    print('Gateway IP address: ', inet_ntoa(giaddr))
    print('Mac address: ', chaddr)
    print(type(chaddr))

    mac_string = binascii.hexlify(chaddr).decode('utf-8')
    client_mac_add = ':'.join(mac_string[i:i + 2] for i in range(0, len(mac_string), 2))
    transaction_id = xid
    chosen_ip = inet_ntoa(struct.unpack('! 4s', packet[-5:-1])[0])
    # print(inet_ntoa(chosen_ip[0]))

    if chosen_ip not in available_addresses:
        print("chosen address not available")
        nak(packet)
        return

    info = {
        "MAC address": client_mac_add,
        "Lease time": LEASE
    }

    log_file[chosen_ip] = info
    available_addresses.remove(chosen_ip)

    ack_packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff", type=0x800) /
            IP(src=SERVER_IP, dst=BROADCAST_IP) /
            UDP(sport=SERVER_PORT, dport=CLIENT_PORT) /
            BOOTP(
                op=OP_REPLY,
                yiaddr=chosen_ip,
                siaddr=SERVER_IP,
                chaddr=mac2str(client_mac_add),
                xid=transaction_id,
            ) /
            DHCP(options=[
                ("message-type", MSG_TYPE_ACK),
                ("server_id", SERVER_IP),
                ("lease_time", LEASE),
                ("broadcast_address", "127.0.0.255"),
                ("router", "10.0.0.1"),
                ("name_server", DNS_SERVER_IP),
                "end"]
            )
    )
    sendp(ack_packet, verbose=False)

def nak(request_packet):
    print("start nak")

    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', request_packet[0:28 + 6])

    mac_string = binascii.hexlify(chaddr).decode('utf-8')
    client_mac_add = ':'.join(mac_string[i:i + 2] for i in range(0, len(mac_string), 2))
    transaction_id = xid
    nak_packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
            IP(src=SERVER_IP, dst=BROADCAST_IP) /
            UDP(sport=SERVER_PORT, dport=CLIENT_PORT) /
            BOOTP(
                op=OP_REPLY,
                siaddr=SERVER_IP,
                chaddr=mac2str(client_mac_add),  # doesn't print the mac address correctly
                xid=transaction_id,
            ) /
            DHCP(options=[
                ("message-type", MSG_TYPE_NAK),
                ("server_id", SERVER_IP),
                "end"]
            )
    )
    sendp(nak_packet, verbose=False)
    print("done nak")


def release(release_packet):
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', release_packet[0:28 + 6])
    client_ip = inet_ntoa(ciaddr)
    if client_ip != "0.0.0.0":
        log_file.pop(client_ip)
        available_addresses.append(client_ip)


def handle_dhcp_packet(dhcp_packet):
    if dhcp_packet[0:2] == b'\x01\x01':
        print("request")
        if dhcp_packet[240:243] == b'5\x01\x01':
            offer(dhcp_packet)

        if dhcp_packet[240:243] == b'5\x01\x03':
            ack(dhcp_packet)

        if dhcp_packet[240:243] == b'5\x01\x07':
            release(dhcp_packet)


def start_server() -> None:
    generate_ip_addresses()  # Creating the database of all the available IP address
    sniffer_socket = socket(AF_INET, SOCK_DGRAM)
    sniffer_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sniffer_socket.bind(('0.0.0.0', 67))
    sniffer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    while True:
        try:
            packet = sniffer_socket.recv(2048)
            print(packet)
            print(packet[0:2])
            print(packet[240:243])
            print(packet[-5:-1])
            handle_dhcp_packet(packet)
        except KeyboardInterrupt:
            print("Shutting down...")
            break

        # b'\x01\x01\x06\x00\
        # x1e@u\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb0\xbe\x83\x1e\n0\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
        # x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00c\x82Sc5\x01\x01=\x06\xb0\xbe\x83\x1e
        # \n07\x03\x03\x01\x06\xff'

if __name__ == '__main__':
    start_server()
