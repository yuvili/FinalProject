import webbrowser

from DHCP_Docs.clientDHCP import ClientDHCP
from DNS_Docs.clientDNS import ClientDNS
from tkinter import *


class Operator:

    def __init__(self):
        # self.dhcp_client = ClientDHCP()
        self.dhcp_client = ClientDHCP()
        self.dns_client = ClientDNS()
        self.window = None
        self.requested = False

    def set_dns_client(self):
        self.dns_client.ip_add = self.dhcp_client.ip_address
        self.dns_client.dns_server_add = self.dhcp_client.dns_server_address
        self.dns_client.subnet_mask = self.dhcp_client.subnet_mask
        self.dns_client.router = self.dhcp_client.router

    def set_window(self, window: Tk):
        self.window = window

    def dhcp_generate_ip(self):
        self.dhcp_client.discover()
        try:
            if not self.dhcp_client.got_offer:
                for i in range(3):
                    if not self.dhcp_client.got_offer:
                        self.dhcp_client.discover()
                    else:
                        break
            if not self.dhcp_client.got_offer:
                return "timeout error"

            print("generated")
            return self.dhcp_client.offered_addr
        except Exception as e:
            print(f"Error: {e}")

    def dhcp_request(self):
        self.dhcp_client.request()
        try:
            while self.dhcp_client.ip_address == "0.0.0.0":
                if self.dhcp_client.got_nak:
                    return "False"
                if not self.dhcp_client.ack_set and not self.dhcp_client.got_nak:
                    return "error"

            if self.dhcp_client.ip_address != "0.0.0.0":
                print("ack")
                return "True"
        except RuntimeError:
            print("RuntimeError")

    def dhcp_decline(self):
        self.dhcp_client.decline()

    def dns_query(self, hostname):
        self.set_dns_client()
        self.dns_client.send_dns_query(hostname, 'A')
        return self.dns_client.ip_result

    def get_image(self):
        # http_tcp_client.start_client()
        print("done html")
        webbrowser.open_new('new_html.html')



