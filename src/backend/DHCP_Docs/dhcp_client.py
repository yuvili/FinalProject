import binascii
import random
import struct
import socket
from socket import *

from getmac import get_mac_address as gma
from datetime import datetime, timedelta

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


class ClientDHCP:

    def __init__(self):
        self.mac_address = gma()  # Extracting the mac address of this computer
        self.ip_address = "0.0.0.0"  # Client's Default IP Address
        self.dns_server_address = ""  # DNS Server IP Address
        self.lease_obtain = None  # Time of obtaining IP address
        self.lease = None
        self.lease_expires= None
        self.subnet_mask = None
        self.router = None

        self.dhcp_server_ip= None
        self.offered_addr= None
        self.transaction_id = None
        self.got_offer = False
        self.got_nak = False
        self.ack_set = False

    def discover(self):
        """
        Broadcast by a DHCP client to locate a DHCP server when the client attempts to claim an IP address.
        """
        self.transaction_id = random.randint(1, 2 ** 32 - 1)

        # Build DHCP discover packet
        op_code = OP_REQUEST
        htype = 1  #Ethernet
        hlen = 6 #Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = inet_pton(AF_INET, self.ip_address)
        yiaddr = inet_pton(AF_INET, self.ip_address)
        siaddr = inet_pton(AF_INET, self.ip_address)
        giaddr = inet_pton(AF_INET, self.ip_address)
        chaddr = binascii.unhexlify(self.mac_address.replace(':', ''))
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

        discover_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                          ciaddr + yiaddr + siaddr + giaddr + chaddr + padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x01' # DHCP message type: 1 = DHCP DISCOVER
        client_id = b'\x3d\x06' + chaddr  # DHCP client identifier: 6 bytes for MAC address
        request_list = b'\x37\x03\x03\x01\x06'  # DHCP parameter request list: requested options are subnet mask, router, DNS server
        end = b'\xff' # end of options marker
        dhcp_options = msg_type + client_id + request_list + end

        # Create a socket object using UDP and bind it to DHCP client port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = discover_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
        server_address = ("255.255.255.255", 67)
        client_socket.sendto(packet, server_address)

        # Receive DHCP OFFER packet from server
        offer_packet = client_socket.recv(2048)
        client_socket.close()

        self.handle_packet(offer_packet)

    def set_offer(self, offer_packet):
        """
        Extract the DHCP OFFER details that were sent from the server.
        :param offer_packet: DHCP server DHCP OFFER packet
        :return:
        """
        op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
            '! B B B B I H H 4s4s4s4s6s', offer_packet[0:34])

        server_id = struct.unpack("! 4s", offer_packet[245: 249])[0]
        self.dhcp_server_ip = inet_ntoa(server_id)
        self.offered_addr = inet_ntoa(yiaddr)
        self.got_offer=True

    def request(self):
        """
        A DHCP Request message broadcasts a message to respond to the DHCP Offer message sent by a DHCP server,
        or in cases when a client wish to renew the IP address lease.
        """

        op_code = OP_REQUEST
        htype = 1  # Ethernet
        hlen = 6  # Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = inet_pton(AF_INET, self.ip_address)
        yiaddr = inet_pton(AF_INET, self.ip_address)
        siaddr = inet_pton(AF_INET, self.ip_address)
        giaddr = inet_pton(AF_INET, self.ip_address)
        chaddr = binascii.unhexlify(self.mac_address.replace(':', ''))
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

        request_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                          ciaddr + yiaddr + siaddr + giaddr + chaddr + \
                          padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x03'  # DHCP message type: 3 = DHCP Request
        server_id = b'\x36\x04' + inet_pton(AF_INET, self.dhcp_server_ip)
        request_addr = b'\x32\x04' + inet_pton(AF_INET, self.offered_addr)
        end = b'\xff'  # end of options marker
        dhcp_options = msg_type + server_id + request_addr + end

        # Create a socket object using UDP and bind it to DHCP client port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = request_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
        client_socket.sendto(packet, ("255.255.255.255", 67))
        # Receive DHCP OFFER packet from server
        ack_packet = client_socket.recv(2048)

        client_socket.close()
        self.handle_packet(ack_packet)

    def decline(self):
        """
        A DHCP Decline message broadcasts a message to respond to the DHCP Offer message sent by a DHCP server,
        in cases the client don't approve of the offered IP address.
        """
        op_code = OP_REQUEST
        htype = 1  # Ethernet
        hlen = 6  # Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = inet_pton(AF_INET, self.ip_address)
        yiaddr = inet_pton(AF_INET, self.ip_address)
        siaddr = inet_pton(AF_INET, self.ip_address)
        giaddr = inet_pton(AF_INET, self.ip_address)
        chaddr = binascii.unhexlify(self.mac_address.replace(':', ''))
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

        decline_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                         ciaddr + yiaddr + siaddr + giaddr + chaddr + \
                         padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x04'  # DHCP message type: 4 = DHCP Decline
        server_id = b'\x36\x04' + inet_pton(AF_INET, self.dhcp_server_ip)
        end = b'\xff'  # end of options marker
        dhcp_options = msg_type + server_id + end

        # Create a socket object using UDP and bind it to DHCP client port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = decline_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
        client_socket.sendto(packet, ("255.255.255.255", 67))
        client_socket.close()

        self.dhcp_server_ip = None
        self.offered_addr = None
        self.transaction_id = None
        self.got_offer = False
        self.got_nak = False
        self.ack_set = False

    def calculate_lease_expire(self, start_time, lease):
        # Convert string to datetime object
        datetime_obj = datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')

        # Add seconds to datetime object
        new_datetime = datetime_obj + timedelta(seconds=lease)

        # Convert datetime object to string
        self.lease_expires = new_datetime.strftime('%d/%m/%Y %H:%M:%S')

    def set_ack(self, ack_packet):
        """
        When receiving a DHCP ACK message, this function is used to extract the details and initilaze them to
        the client.
        :param ack_packet: the received DHCP ACK packet
        """
        op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
            '! B B B B I H H 4s4s4s4s6s', ack_packet[0:34])

        server_id = struct.unpack("! 4s", ack_packet[245: 249])[0]
        lease_time = struct.unpack("! I", ack_packet[251: 255])[0]
        renew_val_time = struct.unpack("! I", ack_packet[257: 261])[0]
        rebinding_time = struct.unpack("! I", ack_packet[262: 266])[0]
        subnet_mask = struct.unpack("! 4s", ack_packet[269: 273])[0]
        broadcast_address = struct.unpack("! 4s", ack_packet[275: 279])[0]
        router = struct.unpack("! 4s", ack_packet[281: 285])[0]
        dns_server = struct.unpack("! 4s", ack_packet[287: 291])[0]

        self.ip_address = inet_ntoa(yiaddr)
        self.subnet_mask = inet_ntoa(subnet_mask)
        self.router = inet_ntoa(router)
        self.dns_server_address = inet_ntoa(dns_server)
        self.lease_obtain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lease = lease_time
        self.calculate_lease_expire(self.lease_obtain, self.lease)
        self.ack_set = True

        self.transaction_id = None
        self.got_offer = False
        self.got_nak = False

    def release(self):
        self.transaction_id = random.randint(1, 2 ** 32 - 1)
        op_code = OP_REQUEST
        htype = 1  # Ethernet
        hlen = 6  # Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = inet_pton(AF_INET, self.ip_address)
        yiaddr = inet_pton(AF_INET, self.ip_address)
        siaddr = inet_pton(AF_INET, self.ip_address)
        giaddr = inet_pton(AF_INET, self.ip_address)
        chaddr = binascii.unhexlify(self.mac_address.replace(':', ''))
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP

        decline_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                         ciaddr + yiaddr + siaddr + giaddr + chaddr + padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x07'  # DHCP message type: 7 = DHCP Release
        end = b'\xff'  # end of options marker
        dhcp_options = msg_type + end

        # Create a socket object using UDP and bind it to DHCP client port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = decline_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 68 (DHCP client port)
        client_socket.sendto(packet, ("255.255.255.255", 67))
        client_socket.close()

        self.ip_address = "0.0.0.0"
        self.dns_server_address = ""  # DNS server IP address
        self.lease_obtain = None
        self.lease = None
        self.lease_expires = None
        self.subnet_mask = None
        self.router = None
        self.dhcp_server_ip = None
        self.offered_addr = None
        self.transaction_id = None
        self.got_offer = False
        self.got_nak = False
        self.ack_set = False

    def handle_packet(self, dhcp_packet):
        if dhcp_packet[0:2] == b'\x02\x01':
            if dhcp_packet[240:243] == b'5\x01\x02':
                print("---------------------")
                print("DHCP Client received a DHCP OFFER packet")
                self.set_offer(dhcp_packet)

            elif dhcp_packet[240:243] == b'5\x01\x05':
                print("---------------------")
                print("DHCP Client received a DHCP ACK packet")
                self.set_ack(dhcp_packet)

            elif dhcp_packet[240:243] == b'5\x01\x06':
                print("---------------------")
                print("DHCP Client received a DHCP NAK packet")
                client_socket = socket(AF_INET, SOCK_DGRAM)
                client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                client_socket.bind(('0.0.0.0', 68))
                try:
                    ack_packet = client_socket.recv(2048)
                    client_socket.close()
                    print(ack_packet)
                    if ack_packet[0:2] == b'\x02\x01':
                        if ack_packet[240:243] == b'5\x01\x05':
                            self.set_ack(dhcp_packet)
                except Exception as e:
                    self.got_nak = True

if __name__ == '__main__':
    client = ClientDHCP()
    client.discover()
