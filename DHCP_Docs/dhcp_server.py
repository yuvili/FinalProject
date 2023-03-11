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
ROUTER_IP = "10.0.0.1"
SERVER_PORT = 67
CLIENT_PORT = 68
SCOPE = 254
LEASE = 86400
BROADCAST_IP = "255.255.255.255"
SUBNET_MASK = "255.255.255.0"
available_addresses = []
log_file = {}
stop = []

def generate_ip_addresses():
    """
    Generate all IP addresses in the range 10.0.0.2 to 10.0.0.254
    """
    for i in range(2, SCOPE):
        available_addresses.append(f"10.0.0.{str(i)}")

def offer(packet):
    """
    A DHCP Offer message is broadcasts a message to respond to the DHCP Discovery message sent by a DHCP client.
    :param packet: DHCP DISCOVERY packet sent by the client
    """
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack('! B B B B I H H 4s4s4s4s6s', packet[0:28+6])

    offered_ip = random.choice(available_addresses)

    op_code = OP_REPLY
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    secs = 0
    flags = 0x0000
    yiaddr = inet_pton(AF_INET, offered_ip)
    siaddr = inet_pton(AF_INET, DNS_SERVER_IP)
    giaddr = inet_pton(AF_INET, ROUTER_IP)
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP

    offer_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                      ciaddr + yiaddr + siaddr + giaddr + chaddr + padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x02'  # DHCP message type: 2 = DHCP OFFER
    server_id = b'\x36\x04' + inet_pton(AF_INET, SERVER_IP)
    lease_time = b'\x33\x04' + LEASE.to_bytes(4, "big")
    renewal_lease_time = b'\x3a\x04' + (int(LEASE/2)).to_bytes(4, "big")
    rebinding_lease_time = b'\x3b\x04' + (int(LEASE*0.75)).to_bytes(4, "big")
    sub_mask = b'\x01\x04' + inet_pton(AF_INET, SUBNET_MASK)
    broadcast_addr = b'\x1c\x04' + inet_pton(AF_INET, BROADCAST_IP)
    router = b'\x03\x04' + inet_pton(AF_INET, ROUTER_IP)
    dns_server = b'\x06\x04' +inet_pton(AF_INET, DNS_SERVER_IP)
    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + server_id + lease_time + renewal_lease_time+ rebinding_lease_time + sub_mask \
                   + broadcast_addr + router + dns_server + end

    # Create a socket object using UDP and bind it to DHCP server port
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    server_socket.bind(("", 67))
    server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # Build the full packet
    packet = offer_header + dhcp_options

    # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
    broadcast_address = ("255.255.255.255", 68)
    server_socket.sendto(packet, broadcast_address)
    server_socket.close()

def ack(request_packet):
    """
    DHCP ACK message is sent as a response to a DHCP REQUEST approving of the client's request.
    :param request_packet: DHCP REQUEST packet sent by the client.
    """

    # Check if the request was sent to this server
    server_id = struct.unpack("! 4s", request_packet[245: 249])[0]
    if inet_ntoa(server_id) != SERVER_IP:
        nak(request_packet) # if client request an address from a different DHCP server
        return

    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', request_packet[0:28 + 6])

    mac_string = binascii.hexlify(chaddr).decode('utf-8')
    client_mac_add = ':'.join(mac_string[i:i + 2] for i in range(0, len(mac_string), 2))
    chosen_ip = inet_ntoa(struct.unpack('! 4s', request_packet[-5:-1])[0])

    # In case when the requested address is not available, send DHCP NAK message
    if chosen_ip not in available_addresses:
        nak(request_packet)
        return

    op_code = OP_REPLY
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    secs = 0
    flags = 0x0000
    yiaddr = inet_pton(AF_INET, chosen_ip)
    siaddr = inet_pton(AF_INET, DNS_SERVER_IP)
    giaddr = inet_pton(AF_INET, ROUTER_IP)
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP

    ack_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                   ciaddr + yiaddr + siaddr + giaddr + chaddr + padding + sname + file + magic_cookie

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

    # Create a socket object using UDP and bind it to DHCP server port
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

    # Adding client details to database and removing the address from the available addresses list
    info = {
        "MAC address": client_mac_add,
        "Lease time": LEASE
    }

    log_file[chosen_ip] = info
    available_addresses.remove(chosen_ip)

def nak(request_packet):
    """
    DHCP NAK message is sent as a response to a DHCP REQUEST when the client chose a different server' IP
    or in cases when the requested IP is not available.
   :param request_packet: DHCP REQUEST packet sent by the client.
    """

    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', request_packet[0:28 + 6])

    op_code = OP_REPLY
    htype = 1  # Ethernet
    hlen = 6  # Address length
    hops = 0
    secs = 0
    flags = 0x0000
    yiaddr = inet_pton(AF_INET, "0.0.0.0")
    siaddr = inet_pton(AF_INET, DNS_SERVER_IP)
    giaddr = inet_pton(AF_INET, ROUTER_IP)
    padding = b'\x00' * 10  # padding (unused)
    sname = b'\x00' * 64  # srchostname
    file = b'\x00' * 128  # bootfilename
    magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP

    nak_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                 ciaddr + yiaddr + siaddr + giaddr + chaddr + padding + sname + file + magic_cookie

    msg_type = b'\x35\x01\x06'  # DHCP message type: 6 = DHCP NAK
    server_id = b'\x36\x04' + inet_pton(AF_INET, SERVER_IP)
    message = b'\x38\x0F' + bytes("wrong server-ID",'utf-8')
    end = b'\xff'  # end of options marker
    dhcp_options = msg_type + server_id + message + end

    # Create a socket object using UDP and bind it to a DHCP server port
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

def release(release_packet):
    """
    When receiving a DHCP Release message, this function is used to remove client from database.
    :param release_packet: DHCP Release message sent from the client.
    """
    op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
        '! B B B B I H H 4s4s4s4s6s', release_packet[0:34])

    client_ip = inet_ntoa(ciaddr)
    log_file.pop(client_ip)
    available_addresses.append(client_ip)

def handle_dhcp_packet(dhcp_packet):
    """
    Handel DHCP client packets
    :param dhcp_packet: DHCP packet sent by the client
    """

    # check if is a OP_REQUEST
    if dhcp_packet[0:2] == b'\x01\x01':
        if dhcp_packet[240:243] == b'5\x01\x01':
            print("---------------------")
            print("Server received a DHCP DISCOVER packet")
            offer(dhcp_packet)

        if dhcp_packet[240:243] == b'5\x01\x03':
            print("---------------------")
            print("Server received a DHCP REQUEST packet")
            ack(dhcp_packet)

        if dhcp_packet[240:243] == b'5\x01\x07':
            print("---------------------")
            print("Server received a DHCP RELEASE packet")
            release(dhcp_packet)

def stop_server():
    stop.append(True)

def start_server() -> None:
    """
    Staring DHCP server to receive packets.
    """
    generate_ip_addresses()  # Creating the database of all the available IP address
    while True:
        if len(stop) != 0 and stop[0]:
            print("Shutting down...")
            break
        try:
            sniffer_socket = socket(AF_INET, SOCK_DGRAM)
            sniffer_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sniffer_socket.bind(('0.0.0.0', 67))
            sniffer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            packet = sniffer_socket.recv(2048)
            sniffer_socket.close()
            handle_dhcp_packet(packet)
        except KeyboardInterrupt:
            print("Shutting down...")
            break
    stop.clear()


if __name__ == '__main__':
    start_server()
