import binascii
import random
import struct
import threading
import socket
from socket import *

from getmac import get_mac_address as gma
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.sendrecv import sendp, sniff
from scapy.utils import mac2str
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
        self.ip_address = "0.0.0.0"  # Client's IP address
        self.dns_server_address = ""  # DNS server IP address
        self.lease_obtain = None
        self.lease = None
        self.lease_expires= None
        self.subnet_mask = None
        self.router = None
        self.client_port = 68
        self.server_port = 67

        self.dhcp_server_ip= None
        self.offered_addr= None
        self.transaction_id = None
        self.got_offer = False
        self.got_nak = False
        self.ack_set = False


    def discover(self):
        """
        Broadcast by a DHCP client to locate a DHCP server when the client attempts to
        connect to a network for the first time.
        """
        # Build DHCP discover packet
        print("in discover")
        self.transaction_id = random.randint(1, 2 ** 32 - 1)
        server_address = ("255.255.255.255", self.server_port)

        op_code = OP_REQUEST
        htype = 1  #Ethernet
        hlen = 6 #Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = self.ip_address
        yiaddr = self.ip_address
        siaddr = self.ip_address
        giaddr = self.ip_address
        chaddr = self.mac_address
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

        mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
        discover_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                          inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                          inet_pton(AF_INET, giaddr) + mac_address_bytes + \
                          padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x01' # DHCP message type: 1 = DHCP DISCOVER
        client_id = b'\x3d\x06' + mac_address_bytes  # DHCP client identifier: 6 bytes for MAC address
        request_list = b'\x37\x03\x03\x01\x06'  # DHCP parameter request list: requested options are subnet mask, router, DNS server

        end = b'\xff' # end of options marker
        dhcp_options = msg_type + client_id + request_list + end

        # Create a socket object using UDP and bind it to a local port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = discover_header + dhcp_options
        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)

        client_socket.sendto(packet, server_address)
        offer_packet = client_socket.recv(2048)
        print(offer_packet)
        # sniff(filter=f'udp and port {self.server_port}', count=1, prn=self.handle_packet, timeout=20)
        #
        # client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 0)
        # client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # client_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        client_socket.close()

        # Sniff DHCP Discover packets and call the callback function
        # packet = sniff(filter=f'udp and port {self.server_port}', count=1, timeout=20)[0]
        self.handle_packet(offer_packet)


    def request(self):
        """
        A DHCP Request message is sent in the following scenarios:
        1. After a DHCP client starts, it broadcasts a DHCP Request message to respond to the DHCP Offer message sent by a DHCP server.
        2. After a DHCP client restarts, it broadcasts a DHCP Request message to confirm the configuration including the allocated IP address.
        3. After a DHCP client obtains an IP address, it unicasts or broadcasts a DHCP Request message to renew the IP address lease.
        :param:
        """
        print("____in request_____")
        op_code = OP_REQUEST
        htype = 1  # Ethernet
        hlen = 6  # Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = self.ip_address
        yiaddr = self.ip_address
        siaddr = self.ip_address
        giaddr = self.ip_address
        chaddr = self.mac_address
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
        server_id = b'\x36\x04' + inet_pton(AF_INET, self.dhcp_server_ip)
        request_addr = b'\x32\x04' + inet_pton(AF_INET, self.offered_addr)
        end = b'\xff'  # end of options marker
        dhcp_options = msg_type + server_id + request_addr + end

        # Create a socket object using UDP and bind it to a local port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = request_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
        client_socket.sendto(packet, ("255.255.255.255", 67))
        ack_packet = client_socket.recv(2048)
        client_socket.close()
        self.handle_packet(ack_packet)

    def sniff(self):
        sniff(filter=f'udp and port {self.server_port} and host {self.dhcp_server_ip}', count=1, prn=self.handle_packet, timeout=20)

    def renew_request(self):
        # After a DHCP client obtains an IP address, it unicasts or broadcasts a DHCP Request message to renew the IP address lease.
        if self.ip_address == "0.0.0.0":
            return

        request_packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff") /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    siaddr=self.ip_address,
                    chaddr=mac2str(self.mac_address),
                    xid=random.randint(1, 2 ** 32 - 1)
                ) /
                DHCP(options=[
                    ("message-type", MSG_TYPE_REQUEST),
                    ("server_id", self.router),
                    ("requested_addr", self.ip_address), "end"]
                )
        )
        sendp(request_packet, verbose=False)

    def calculate_lease_expire(self, start_time, lease):
        # Convert string to datetime object
        datetime_obj = datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')

        # Add seconds to datetime object
        new_datetime = datetime_obj + timedelta(seconds=lease)

        # Convert datetime object to string
        self.lease_expires = new_datetime.strftime('%d/%m/%Y %H:%M:%S')

    def set_ack(self, ack_packet):
        op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
            '! B B B B I H H 4s4s4s4s6s', ack_packet[0:34])

        server_id, lease_time, renew_val_time, rebinding_time, subnet_mask, broadcast_address, router, \
            dns_server = struct.unpack("! 4s I I I 4s 4s 4s 4s", ack_packet[243: 275])

        self.ip_address = inet_ntoa(server_id)
        self.subnet_mask = inet_ntoa(subnet_mask)
        self.router = inet_ntoa(router)
        self.dns_server_address = inet_ntoa(dns_server)
        self.lease_obtain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lease = lease_time
        self.calculate_lease_expire(self.lease_obtain, self.lease)
        self.ack_set = True

    def decline(self):
        op_code = OP_REQUEST
        htype = 1  # Ethernet
        hlen = 6  # Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = self.ip_address
        yiaddr = self.ip_address
        siaddr = self.ip_address
        giaddr = self.ip_address
        chaddr = self.mac_address
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

        mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
        decline_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                         inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                         inet_pton(AF_INET, giaddr) + mac_address_bytes + \
                         padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x04'  # DHCP message type: 3 = DHCP Request
        server_id = b'\x36\x04' + inet_pton(AF_INET, self.dhcp_server_ip)
        end = b'\xff'  # end of options marker
        dhcp_options = msg_type + server_id + end

        # Create a socket object using UDP and bind it to a local port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = decline_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
        client_socket.sendto(packet, ("255.255.255.255", 67))
        client_socket.close()

    def release(self):
        self.transaction_id = random.randint(1, 2 ** 32 - 1)
        op_code = OP_REQUEST
        htype = 1  # Ethernet
        hlen = 6  # Address length
        hops = 0
        xid = self.transaction_id
        secs = 0
        flags = 0x0000
        ciaddr = self.ip_address
        yiaddr = self.ip_address
        siaddr = self.ip_address
        giaddr = self.ip_address
        chaddr = self.mac_address
        padding = b'\x00' * 10  # padding (unused)
        sname = b'\x00' * 64  # srchostname
        file = b'\x00' * 128  # bootfilename
        magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99

        mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
        decline_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                         inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                         inet_pton(AF_INET, giaddr) + mac_address_bytes + \
                         padding + sname + file + magic_cookie

        msg_type = b'\x35\x01\x07'  # DHCP message type: 3 = DHCP Request
        end = b'\xff'  # end of options marker
        dhcp_options = msg_type + end

        # Create a socket object using UDP and bind it to a local port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # Build the full packet
        packet = decline_header + dhcp_options

        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)
        client_socket.sendto(packet, ("255.255.255.255", 67))
        client_socket.close()

    def inform(self, dns_addr: str = None, gateway: str = None):
        pass

    def offer(self, offer_packet):
        op_code, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr = struct.unpack(
            '! B B B B I H H 4s4s4s4s6s', offer_packet[0:34])

        server_id, lease_time, renew_val_time, rebinding_time, subnet_mask, broadcast_address, router, \
            dns_server = struct.unpack("! 4s I I I 4s 4s 4s 4s", offer_packet[243: 275])
        self.dhcp_server_ip = inet_ntoa(server_id)
        self.offered_addr = inet_ntoa(yiaddr)
        self.got_offer=True

    def handle_packet(self, dhcp_packet):
        if dhcp_packet[0:2] == b'\x02\x01':
            print("reply")
            print(dhcp_packet[240:243])
            if dhcp_packet[240:243] == b'5\x01\x02':
                print("offer")
                print(dhcp_packet)
                self.offer(dhcp_packet)

            elif dhcp_packet[240:243] == b'5\x01\x05':
                self.set_ack(dhcp_packet)

            elif dhcp_packet[240:243] == b'5\x01\x06':
                client_socket = socket(AF_INET, SOCK_DGRAM)
                client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                client_socket.bind(('0.0.0.0', 68))

                ack_packet = client_socket.recv(2048)
                client_socket.close()
                print(ack_packet)
                if ack_packet[0:2] == b'\x02\x01':
                    if ack_packet[240:243] == b'5\x01\x05':
                        self.set_ack(dhcp_packet)


if __name__ == '__main__':
    client = ClientDHCP()
    client.discover()
