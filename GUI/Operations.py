import threading
from time import sleep

from DHCP_Docs.dhcp_client import ClientDHCP
from DNS_Docs.dns_client import ClientDNS
from tkinter import *


class Operator:

    def __init__(self):
        self.dhcp_client = ClientDHCP()
        self.dns_client = ClientDNS()
        self.window = None
        self.requested = False

    def set_dns_client(self):
        self.dns_client.ip_add = self.dhcp_client.ip_add
        self.dns_client.dns_server_add = self.dhcp_client.dns_server_add
        self.dns_client.subnet_mask = self.dhcp_client.subnet_mask
        self.dns_client.router = self.dhcp_client.router

    def set_window(self, window: Tk):
        self.window = window

    def dhcp_generate_ip(self):
        self.dhcp_client.discover()
        try:
            while not self.dhcp_client.got_offer:
                print("didnt get offer")
                self.dhcp_client.discover()

            print("generated")
            return self.dhcp_client.offered_addr
        except Exception as e:
            print(f"Error: {e}")

    def dhcp_request(self):
        self.dhcp_client.request()
        try:
            while self.dhcp_client.ip_add == "0.0.0.0":
                if self.dhcp_client.got_nak:
                    return False
                if not self.dhcp_client.ack_set and not self.dhcp_client.got_nak:
                    self.dhcp_client.request()

            if self.dhcp_client.ip_add != "0.0.0.0":
                print("ack")
                return True
        except RuntimeError:
            print("RuntimeError")

    def dhcp_decline(self):
        self.dhcp_client.decline()

    def dns_query(self, hostname):
        self.set_dns_client()
        self.dns_client.send_dns_query(hostname)
        return self.dns_client.ip_result



