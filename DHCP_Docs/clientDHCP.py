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

        # Define the IP and UDP header fields
        # version = 4  # IPv4
        # header_length = 5  # 20 bytes
        # ttl = 64  # Time-to-live
        # protocol = 17  # UDP
        # ip_source = '0.0.0.0'
        # ip_dest = '255.255.255.0'

        # udp_source_port = self.client_port
        # udp_dest_port = self.server_port

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


        # discover_header = struct.pack('! B', op_code)
        # discover_header1 = struct.pack('! B ', htype)
        # discover_header2 = struct.pack('! B', hlen)
        # discover_header3 = struct.pack('! B', hops)
        # discover_header4 = struct.pack('! I', xid)
        # discover_header5 = struct.pack('! H', secs)
        # discover_header6 = struct.pack('! H ', flags)
        # discover_header7 = struct.pack('! I', ciaddr)
        # discover_header8 = struct.pack('! I', yiaddr)
        # discover_header9 = struct.pack('! I', siaddr)
        # discover_header10 = struct.pack('! I', giaddr)


        msg_type = b'\x35\x01\x01' # DHCP message type: 1 = DHCP DISCOVER
        # par_req_list = b'\x37\x0d\x01\x1c\x02\x03\x0f\x06\x77\x0c\x2c\x2f\x1a\x79\x2a'
        client_id = b'\x3d\x06' + mac_address_bytes  # DHCP client identifier: 6 bytes for MAC address
        request_list = b'\x37\x03\x03\x01\x06'  # DHCP parameter request list: requested options are subnet mask, router, DNS server
        # request_list = struct.pack('! B B B B B', 55, 3, 1, 3, 6)  # Requested parameters (subnet mask, router, DNS server)

        end = b'\xff' # end of options marker
        dhcp_options = msg_type + client_id + request_list + end

        # # Define the DHCP message fields
        # dhcp_message_type = 1  # DHCPDISCOVER
        # dhcp_client_mac = b'\x00\x11\x22\x33\x44\x55'  # Client MAC address
        #
        # # Build the DHCP options field
        # dhcp_options = struct.pack('!BBB', 53, 1, dhcp_message_type)  # DHCP message type
        # dhcp_options += struct.pack('!BB6s', 61, 7, dhcp_client_mac)  # Client identifier
        # dhcp_options += struct.pack('!BBB', 55, 3, 1, 3, 6)  # Requested parameters (subnet mask, router, DNS server)

        # Calculate the UDP length
        # udp_length = 8 + len(dhcp_options)  # Length in bytes of the UDP datagram (excluding the header)
        # udp_checksum = 0  # Optional checksum, set to 0
        #
        # # Build the UDP header
        # udp_header = struct.pack('!HHH', udp_source_port, udp_dest_port, udp_length)
        # udp_header += struct.pack('!H', udp_checksum)  # Optional checksum, set to 0

        # Build the IP header
        # ip_total_length = header_length * 4 + len(udp_header) + len(dhcp_options)
        # ip_header = struct.pack('!BBHHHBBH4s4s', (version << 4) + header_length,  # Version and header length
        #                         0,  # Type of service (not used)
        #                         ip_total_length,  # Total length
        #                         0,  # Identification (not used)
        #                         0,  # Flags and fragment offset (not used)
        #                         ttl,  # Time-to-live
        #                         protocol,  # Protocol
        #                         0,  # Header checksum (not used)
        #                         inet_aton(ip_source),  # Source IP address
        #                         inet_aton(ip_dest))  # Destination IP address


        # Create a socket object using UDP and bind it to a local port
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', 68))

        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # client_socket.bind(("0.0.0.0", 68))
        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)
        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"eth0")

        # Build the full packet
        packet = discover_header + dhcp_options
        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)

        client_socket.sendto(packet, server_address)

        client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 0)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        client_socket.close()
        #
        # sniffer_socket = socket(AF_INET, SOCK_DGRAM)
        # sniffer_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # sniffer_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # sniffer_socket.bind(('0.0.0.0', 68))


        # Sniff DHCP Discover packets and call the callback function

        packet = sniff(filter=f'udp and port {self.server_port}', count=1, timeout=20)[0]
        self.handle_packet(packet)

    def request(self):
        """
        A DHCP Request message is sent in the following scenarios:
        1. After a DHCP client starts, it broadcasts a DHCP Request message to respond to the DHCP Offer message sent by a DHCP server.
        2. After a DHCP client restarts, it broadcasts a DHCP Request message to confirm the configuration including the allocated IP address.
        3. After a DHCP client obtains an IP address, it unicasts or broadcasts a DHCP Request message to renew the IP address lease.
        :param:
        """

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
        discover_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
                          inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
                          inet_pton(AF_INET, giaddr) + mac_address_bytes + \
                          padding + sname + file + magic_cookie


        msg_type = b'\x35\x01\x03'  # DHCP message type: 3 = DHCP Request
        client_id = b'\x3d\x06' + mac_address_bytes  # DHCP client identifier: 6 bytes for MAC address
        # request_list = b'\x37\x03\x03\x01\x06'  # DHCP parameter request list: requested options are subnet mask, router, DNS server
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
        packet = discover_header + dhcp_options
        # Send the packet to the broadcast address on UDP port 67 (DHCP server port)

        client_socket.sendto(packet, ("255.255.255.255", 67))
        client_socket.close()

        packet = sniff(filter=f'udp and port {self.server_port} and host {self.dhcp_server_ip}', count=1, timeout=20)[0]
        self.handle_packet(packet)

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

    def set_ack(self, dhcp_ack):
        self.ip_address = dhcp_ack[BOOTP].yiaddr
        self.subnet_mask = dhcp_ack[DHCP].options[3][1]
        self.router = dhcp_ack[DHCP].options[4][1]
        self.dns_server_address = dhcp_ack[DHCP].options[5][1]
        self.lease_obtain = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lease = dhcp_ack[DHCP].options[2][1]
        self.calculate_lease_expire(self.lease_obtain, self.lease)
        self.ack_set = True

    def decline(self):
        decline_packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff") /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    siaddr=self.ip_address,
                    chaddr=mac2str(self.mac_address),
                    xid=self.transaction_id
                ) /
                DHCP(options=[
                    ("message-type", MSG_TYPE_DECLINE),
                    ("server_id", self.dhcp_server_ip), "end"]
                )
        )
        sendp(decline_packet, verbose=False)

    def release(self):
        self.transaction_id = random.randint(1, 2 ** 32 - 1)
        # server_address = ("255.255.255.0", self.server_port)
        #
        # op_code = OP_REQUEST
        # htype = 1  # Ethernet
        # hlen = 6  # Address length
        # hops = 0
        # xid = self.transaction_id
        # secs = 0
        # flags = 0x0000
        # ciaddr = self.ip_address
        # yiaddr = self.ip_address
        # siaddr = self.ip_address
        # giaddr = self.ip_address
        # chaddr = self.mac_address
        # padding = b'\x00' * 10  # padding (unused)
        # sname = b'\x00' * 64  # srchostname
        # file = b'\x00' * 128  # bootfilename
        # magic_cookie = b'\x63\x82\x53\x63'  # magic cookie: DHCP option 99, 130, 83, 99
        #
        # mac_address_bytes = binascii.unhexlify(chaddr.replace(':', ''))
        # discover_header = struct.pack('! B B B B I H H', op_code, htype, hlen, hops, xid, secs, flags) + \
        #                   inet_pton(AF_INET, ciaddr) + inet_pton(AF_INET, yiaddr) + inet_pton(AF_INET, siaddr) + \
        #                   inet_pton(AF_INET, giaddr) + mac_address_bytes + \
        #                   padding + sname + file + magic_cookie
        #
        # msg_type = b'\x35\x01\x07'  # DHCP message type: 1 = DHCP DISCOVER
        # end = b'\xff'  # end of options marker
        # dhcp_options = msg_type + end
        #
        # # Create a socket object using UDP and bind it to a local port
        # client_socket = socket(AF_INET, SOCK_DGRAM)
        # client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # client_socket.bind((self.ip_address, 68))
        #
        #
        # # Build the full packet
        # packet = discover_header + dhcp_options
        #
        # client_socket.sendto(packet, server_address)
        # client_socket.close()
        # self.ip_address = "0.0.0.0"

        packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
                IP(src=self.ip_address, dst=self.router) /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    chaddr=mac2str(self.mac_address),
                    xid=random.randint(1, 2 ** 32 - 1),
                ) /
                DHCP(options=[("message-type", MSG_TYPE_RELEASE), "end"])
        )
        self.ip_address = "0.0.0.0"
        sendp(packet, verbose=False)

    def inform(self, dns_addr: str = None, gateway: str = None):
        pass

    def offer(self, offer_packet):
        self.dhcp_server_ip = offer_packet[IP].src
        self.offered_addr = offer_packet[BOOTP].yiaddr
        self.got_offer=True

    def handle_packet(self, dhcp_packet):
        if DHCP in dhcp_packet:
            dhcp_packet.show()

            # Match DHCP offer
            if dhcp_packet[DHCP].options[0][1] == MSG_TYPE_OFFER:
                print('---')
                print('New DHCP Offer')
                self.offer(dhcp_packet)
                # self.request()
                return

            # Match DHCP ack
            elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_ACK and dhcp_packet[IP].src == self.dhcp_server_ip:
                print('---')
                print('New DHCP ACK')
                self.got_offer = False
                self.set_ack(dhcp_packet)
                return

            # Match DHCP nak
            elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_NAK and dhcp_packet[IP].src == self.dhcp_server_ip:
                print('---')
                print('New DHCP NAK')
                self.got_nak = True
                self.dhcp_server_ip = None
                self.offered_addr = None
                self.got_offer = False
                return
        return

    def sniff_for_ack(self) -> None:
        try:
            print("in sniff")
            packet = sniff(filter=f'udp and port {self.server_port} and host {self.dhcp_server_ip}', count=1, timeout=20)
            thread = threading.Thread(target=self.handle_packet, args=packet)
            thread.start()
            thread.join()
        except KeyboardInterrupt:
            print("Shutting down...")

        except Exception as e:
            print(f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    client = ClientDHCP()
    client.discover()
