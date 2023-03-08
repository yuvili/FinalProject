import threading
from time import sleep

from DHCP_Docs.dhcp_client import ClientDHCP
from DNS_Docs.dns_client import ClientDNS
from tkinter import *


class Operator:

    def __init__(self):
        self.dhcp_client = ClientDHCP()
        # self.dns_client = ClientDNS()
        self.window = None
        self.requested = False

    def set_window(self, window: Tk):
        self.window = window

    def dhcp_generate_ip(self):
        self.dhcp_client.discover()
        self.dhcp_client.start_sniff()
        try:
            while not self.dhcp_client.got_offer:
                sleep(2)

            print("generated")
            return self.dhcp_client.offered_addr
        except RuntimeError:
            print("RuntimeError")

    def dhcp_request(self):
        self.dhcp_client.request()
        self.dhcp_client.start_sniff()
        try:
            while self.dhcp_client.ip_add == "0.0.0.0":
                sleep(2)
                if self.dhcp_client.got_nak:
                    return False

            if self.dhcp_client.ip_add != "0.0.0.0":
                print("ack")
                return True
        except RuntimeError:
            print("RuntimeError")

    def dhcp_decline(self):
        self.dhcp_client.decline()

    def clear_screen(self, screen):
        for widgets in screen.winfo_children():
            widgets.destroy()



