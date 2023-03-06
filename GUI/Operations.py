from DHCP_Docs.dhcp_client import ClientDHCP
from DNS_Docs.dns_client import ClientDNS
from DHCP_Docs import dhcp_server
from DNS_Docs import dns_server
from tkinter import *



class Operator:

    def __init__(self):
        self.dhcp_client = ClientDHCP()
        # self.dns_client = ClientDNS()
        self.window = None

    def set_window(self, window: Tk):
        self.window = window

    def dhcp_generate_ip(self, dhcp_window):
        self.dhcp_client.start_client()
        offered_ip = Label(dhcp_window, text=f"You got the IP:{self.dhcp_client.ip_add}")
        offered_ip.pack()

