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
        # dhcp_server.start_server()

    def set_window(self, window: Tk):
        self.window = window

    def dhcp_generate_ip(self, gen_ip_screen):
        self.dhcp_client.discover()

        Label(gen_ip_screen, text="").pack()
        Button(gen_ip_screen, text="Approve", width=9, height=1,
               command=lambda: self.dhcp_request()).place(relx=0.3, rely=0.4, anchor=CENTER)
        Button(gen_ip_screen, text="Decline", width=9, height=1,
               command=lambda: self.dhcp_decline()).place(relx=0.7, rely=0.4, anchor=CENTER)

        offered_ip = Label(gen_ip_screen, text=f"You got the IP:{self.dhcp_client.ip_add}")
        offered_ip.pack()

    def dhcp_request(self):
        pass

    def dhcp_decline(self):
        pass

