import random
import threading

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
        self.ip_add = "0.0.0.0"  # Client's IP address
        self.dns_server_add = ""  # DNS server IP address
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
        packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    chaddr=mac2str(self.mac_address),
                    xid=self.transaction_id,
                ) /
                DHCP(options=[("message-type", MSG_TYPE_DISCOVER), "end"])
        )

        thread_ack = threading.Thread(target=self.start_sniff)
        thread_ack.start()
        sendp(packet, verbose=False)
        thread_ack.join()

    def request(self):
        """
        A DHCP Request message is sent in the following scenarios:
        1. After a DHCP client starts, it broadcasts a DHCP Request message to respond to the DHCP Offer message sent by a DHCP server.
        2. After a DHCP client restarts, it broadcasts a DHCP Request message to confirm the configuration including the allocated IP address.
        3. After a DHCP client obtains an IP address, it unicasts or broadcasts a DHCP Request message to renew the IP address lease.
        :param:
        """

        request_packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff") /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    siaddr=self.ip_add,
                    chaddr=mac2str(self.mac_address),
                    xid=self.transaction_id
                ) /
                DHCP(options=[
                    ("message-type", MSG_TYPE_REQUEST),
                    ("server_id", self.dhcp_server_ip),
                    ("requested_addr", self.offered_addr), "end"]
                )
        )
        thread_ack = threading.Thread(target=self.sniff_for_ack)
        thread_ack.start()
        sendp(request_packet, verbose=False)
        thread_ack.join()

    def renew_request(self):
        # After a DHCP client obtains an IP address, it unicasts or broadcasts a DHCP Request message to renew the IP address lease.
        if self.ip_add == "0.0.0.0":
            return

        request_packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff") /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    siaddr=self.ip_add,
                    chaddr=mac2str(self.mac_address),
                    xid=random.randint(1, 2 ** 32 - 1)
                ) /
                DHCP(options=[
                    ("message-type", MSG_TYPE_REQUEST),
                    ("server_id", self.router),
                    ("requested_addr", self.ip_add), "end"]
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
        self.ip_add = dhcp_ack[BOOTP].yiaddr
        self.subnet_mask = dhcp_ack[DHCP].options[3][1]
        self.router = dhcp_ack[DHCP].options[4][1]
        self.dns_server_add = dhcp_ack[DHCP].options[5][1]
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
                    siaddr=self.ip_add,
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
        packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
                IP(src=self.ip_add, dst=self.router) /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    chaddr=mac2str(self.mac_address),
                    xid=random.randint(1, 2 ** 32 - 1),
                ) /
                DHCP(options=[("message-type", MSG_TYPE_RELEASE), "end"])
        )
        self.ip_add = "0.0.0.0"
        sendp(packet, verbose=False)

    def inform(self, dns_addr: str = None, gateway: str = None):
        pass

    def offer(self, offer_packet):
        self.dhcp_server_ip = offer_packet[IP].src
        self.offered_addr = offer_packet[BOOTP].yiaddr
        self.got_offer=True

    def handle_packet(self, dhcp_packet=None):
        print("after sniff")
        if dhcp_packet is None:
            print("no package")
            return

        if DHCP in dhcp_packet:
            dhcp_packet.show()

            # Match DHCP offer
            if dhcp_packet[DHCP].options[0][1] == MSG_TYPE_OFFER:
                print('---')
                print('New DHCP Offer')
                self.offer(dhcp_packet)
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
    def start_sniff(self) -> None:
        try:
            print("in sniff")
            packet = sniff(filter=f'udp and port {self.server_port}', count=1, timeout=20)
            thread = threading.Thread(target=self.handle_packet, args=packet)
            thread.start()
            thread.join()
        except KeyboardInterrupt:
            print("Shutting down...")

        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    client = ClientDHCP()
    client.start_sniff()
