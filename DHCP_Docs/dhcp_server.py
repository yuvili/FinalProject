# Scope - how many IP addresses are available
# Database to store IP, Mac add, Device name
# Lease time - Thread that always checks TTL for the IP address

import threading
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import *
from scapy.utils import mac2str
import random

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
    if packet[IP].src != "0.0.0.0":
        return
    client_mac_add = packet[Ether].src
    offered_ip = random.choice(available_addresses)
    transaction_id = packet[BOOTP].xid
    offer_packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff", type=0x0800) /
            IP(src=SERVER_IP, dst=offered_ip) /
            UDP(sport=SERVER_PORT, dport=CLIENT_PORT) /
            BOOTP(
                op=OP_REPLY,
                yiaddr=offered_ip,
                siaddr=SERVER_IP,
                chaddr=mac2str(client_mac_add),  # doesn't print the mac address correctly
                xid=transaction_id,
            ) /
            DHCP(options=[
                ("message-type", MSG_TYPE_OFFER),
                ("server_id", SERVER_IP),
                ("lease_time", LEASE),
                ("subnet_mask", "255.255.255.0"),
                ("router", "10.0.0.1"),
                ("name_server", "10.0.0.1"),
                ("domain", "localdomain"),
                "end"]
            )
    )
    sendp(offer_packet, verbose=False)
    print("done offer")


def ack(packet):
    client_mac_add = packet[Ether].src
    transaction_id = packet[BOOTP].xid
    chosen_ip = packet[DHCP].options[2][1]

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
                ("name_server", "10.0.0.1"),
                "end"]
            )
    )
    sendp(ack_packet, verbose=False)


def nak(request_packet):
    print("start nak")

    client_mac_add = request_packet[Ether].src
    transaction_id = request_packet[BOOTP].xid
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
    client_ip = release_packet[IP].src
    if client_ip != "0.0.0.0":
        log_file.pop(client_ip)
        available_addresses.append(client_ip)


def handle_dhcp_packet(dhcp_packet):
    if DHCP in dhcp_packet:
        if available_addresses is None:
            nak(dhcp_packet)
            return

        # Match DHCP discover
        if dhcp_packet[DHCP].options[0][1] == MSG_TYPE_DISCOVER:
            print('---')
            print('New DHCP Discover')
            offer(dhcp_packet)

        # Match DHCP request
        elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_REQUEST:
            for op in dhcp_packet[DHCP].options:
                if op[0] == "server_id":
                    if op[1] != SERVER_IP:
                        print('---')
                        print('New DHCP Request to different server')
                        nak(dhcp_packet)
                        return
            print('---')
            print('New DHCP Request')
            ack(dhcp_packet)

        # Match DHCP release
        elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_RELEASE:
            print('---')
            print('New DHCP Release')
            release(dhcp_packet)

        # Match DHCP decline
        elif dhcp_packet[DHCP].options[0][1] == MSG_TYPE_DECLINE:
            print('---')
            print('New DHCP Decline')

    else:
        print('---')
        print('Some Other UDP Packet')
        print(dhcp_packet.summary())


def start_server() -> None:
    threads = []
    generate_ip_addresses()  # Creating the database of all the available IP address
    while True:
        try:
            packet = sniff(filter=f'udp and port {CLIENT_PORT}', count=1)
            thread = threading.Thread(target=handle_dhcp_packet, args=packet)
            thread.start()
            threads.append(thread)
        except KeyboardInterrupt:
            print("Shutting down...")
            break

    for thread in threads:  # Wait for all threads to finish
        thread.join()

if __name__ == '__main__':
    start_server()
