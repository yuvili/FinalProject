import random
from getmac import get_mac_address as gma
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.sendrecv import sendp, sniff
from scapy.utils import mac2str

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
        self.subnet_mask = None
        self.router = None
        self.client_port = 68
        self.server_port = 67

    def discover(self):
        """
        Broadcast by a DHCP client to locate a DHCP server when the client attempts to
        connect to a network for the first time.
        """
        # Build DHCP discover packet
        print("in discover")
        packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    chaddr=mac2str(self.mac_address),
                    xid=random.randint(1, 2 ** 32 - 1),
                ) /
                DHCP(options=[("message-type", MSG_TYPE_DISCOVER), "end"])
        )
        sendp(packet, verbose=False)
        print("send packet")
        while True:
            pack = sniff(filter='udp and port 67', count=1)
            if DHCP in pack:
                pack.show()
                # Match DHCP offer
                if pack[DHCP].options[0][1] == MSG_TYPE_OFFER:
                    print('---')
                    print('New DHCP Offer')
                    # TODO-2: get results form offer func and make this function a return to return the ip address
                    self.offer(pack)

    def request(self, server_ip, offered_addr, transaction_id):
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
                    xid=transaction_id
                ) /
                DHCP(options=[
                    ("message-type", MSG_TYPE_REQUEST),
                    ("server_id", server_ip),
                    ("requested_addr", offered_addr), "end"]
                )
        )
        sendp(request_packet, verbose=False)

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

    def set_ack(self, dhcp_ack):
        self.ip_add = dhcp_ack[BOOTP].yiaddr
        self.subnet_mask = dhcp_ack[DHCP].options[3][1]
        self.router = dhcp_ack[DHCP].options[4][1]

    def decline(self, dhcp_offer):
        server_ip = dhcp_offer[IP].src
        transaction_id = dhcp_offer[BOOTP].xid

        decline_packet = (
                Ether(dst="ff:ff:ff:ff:ff:ff") /
                IP(src="0.0.0.0", dst="255.255.255.255") /
                UDP(sport=68, dport=67) /
                BOOTP(
                    op=OP_REQUEST,
                    siaddr=self.ip_add,
                    chaddr=mac2str(self.mac_address),
                    xid=transaction_id
                ) /
                DHCP(options=[
                    ("message-type", MSG_TYPE_DECLINE),
                    ("server_id", server_ip), "end"]
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
        server_ip = offer_packet[IP].src
        offered_addr = offer_packet[BOOTP].yiaddr
        transaction_id = offer_packet[BOOTP].xid

        return server_ip, offered_addr, transaction_id

    def handle_offer(self, dhcp_packet):
        print("after sniff")

        if DHCP in dhcp_packet:
            dhcp_packet.show()
            # Match DHCP offer
            if dhcp_packet[DHCP].options[0][1] == MSG_TYPE_OFFER:
                print('---')
                print('New DHCP Offer')
                self.offer(dhcp_packet)

            # Match DHCP ack
            elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_ACK:
                print('---')
                print('New DHCP ACK')
                self.set_ack(dhcp_packet)

            # Match DHCP ack
            elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_NAK:
                print('---')
                print('New DHCP NAK')

    def start_client(self) -> None:
        self.discover()
        print("after discover")
        while True:
            try:
                sniff(filter='udp and port 67', prn=self.handle_offer, count=1)

            except Exception as e:
                print(f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    client = ClientDHCP()
    client.start_client()
