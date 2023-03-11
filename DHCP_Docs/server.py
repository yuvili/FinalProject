# Scope - how many IP addresses are available
# Database to store IP, Mac add, Device name
# Lease time - Thread that always checks TTL for the IP address
import binascii
import struct
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

def offer(packet):
    print("start offer")
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack('! B B B B I H H 4s4s4s4s6s', packet[0:28+6])

    offered_ip = random.choice(available_addresses)
    transaction_id = xid
    print(transaction_id)

    op_code = OP_REPLY
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    secs = 0
    flags = 0x0000
    yiaddr = offered_ip
    siaddr = DNS_SERVER_IP
    giaddr = DNS_SERVER_IP  # change
    chaddr = chaddr
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

    # mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
    offer_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                      ciaddr + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                      inet_pton(AF_INET, giaddr) + chaddr + padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x02'  # DHCP message type: 1 = DHCP DISCOVER
    server_id = b'\x36\x04' + inet_pton(AF_INET, SERVER_IP)
    lease_time = b'\x33\x04' + LEASE.to_bytes(4, "big")
    renewal_lease_time = b'\x3a\x04' + LEASE.to_bytes(4, "big")
    rebinding_lease_time = b'\x3b\x04' + LEASE.to_bytes(4, "big")
    sub_mask = b'\x01\x04' + inet_pton(AF_INET, "255.255.255.0")
    broadcast_addr = b'\x1c\x04' + inet_pton(AF_INET, "10.0.0.255")
    router = b'\x03\x04' + inet_pton(AF_INET, DNS_SERVER_IP)
    dns_server = b'\x06\x04' +inet_pton(AF_INET, DNS_SERVER_IP)
    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + server_id + lease_time + renewal_lease_time+ rebinding_lease_time + sub_mask \
                   + broadcast_addr + router + dns_server + end

    # Create a socket object using UDP and bind it to a local port
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    server_socket.bind(("", 67))
    server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # Build the full packet
    packet = offer_header + dhcp_options

    # Send the packet to the broadcast address on UDP port 68 (DHCP client port)
    broadcast_address = ("255.255.255.255", 68)
    server_socket.sendto(packet, broadcast_address)
    server_socket.close()
    start_server()
    print("done offer")

def ack(packet):
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', packet[0:28 + 6])

    mac_string = binascii.hexlify(chaddr).decode('utf-8')
    client_mac_add = ':'.join(mac_string[i:i + 2] for i in range(0, len(mac_string), 2))
    chosen_ip = inet_ntoa(struct.unpack('! 4s', packet[-5:-1])[0])

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

    op_code = OP_REPLY
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    secs = 0
    flags = 0x0000
    yiaddr = chosen_ip
    siaddr = DNS_SERVER_IP
    giaddr = DNS_SERVER_IP  # change
    chaddr = chaddr
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

    ack_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                   ciaddr + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                   inet_pton(AF_INET, giaddr) + chaddr + padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x05'  # DHCP message type: 5 = DHCP ACK
    server_id = b'\x36\x04' + inet_pton(AF_INET, SERVER_IP)
    lease_time = b'\x33\x04' + LEASE.to_bytes(4, "big")
    renewal_lease_time = b'\x3a\x04' + LEASE.to_bytes(4, "big")
    rebinding_lease_time = b'\x3b\x04' + LEASE.to_bytes(4, "big")
    sub_mask = b'\x01\x04' + inet_pton(AF_INET, "255.255.255.0")
    broadcast_addr = b'\x1c\x04' + inet_pton(AF_INET, "10.0.0.255")
    router = b'\x03\x04' + inet_pton(AF_INET, DNS_SERVER_IP)
    dns_server = b'\x06\x04' + inet_pton(AF_INET, DNS_SERVER_IP)
    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + server_id + lease_time + renewal_lease_time + rebinding_lease_time + sub_mask \
                   + broadcast_addr + router + dns_server + end

    # Create a socket object using UDP and bind it to a local port
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    server_socket.bind(("", 67))
    server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # Build the full packet
    packet = ack_header + dhcp_options

    # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
    broadcast_address = ("255.255.255.255", 68)
    server_socket.sendto(packet, broadcast_address)
    server_socket.close()


def nak(request_packet):
    print("start nak")

    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', request_packet[0:28 + 6])

    op_code = OP_REPLY
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    secs = 0
    flags = 0x0000
    siaddr = DNS_SERVER_IP
    giaddr = DNS_SERVER_IP  # change
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

    nak_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                 ciaddr + yiaddr + inet_pton(AF_INET, siaddr) + \
                 inet_pton(AF_INET, giaddr) + chaddr + padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x06'  # DHCP message type: 5 = DHCP ACK
    server_id = b'\x36\x04' + inet_pton(AF_INET, SERVER_IP)
    message = b'\x38\x0F' + bytes("wrong server-ID",'utf-8')

    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + server_id + message + end

    # Create a socket object using UDP and bind it to a local port
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    server_socket.bind(("", 67))
    server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # Build the full packet
    packet = nak_header + dhcp_options

    # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
    broadcast_address = ("255.255.255.255", 68)
    server_socket.sendto(packet, broadcast_address)
    server_socket.close()
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
    while True:
        try:
            sniffer_socket = socket(AF_INET, SOCK_DGRAM)
            sniffer_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sniffer_socket.bind(('0.0.0.0', 67))
            sniffer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            packet = sniffer_socket.recv(2048)
            # print(packet)
            # print(packet[0:2])
            # print(packet[240:243])
            # print(packet[-5:-1])
            sniffer_socket.close()
            handle_dhcp_packet(packet)
        except KeyboardInterrupt:
            print("Shutting down...")
            break


if __name__ == '__main__':
    start_server()
