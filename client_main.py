from getmac import get_mac_address as gma


class Client:

    def __init__(self):
        self.mac_address = gma()  # Extracting the mac address of this computer
        self.ip_add = "0.0.0.0"  # Client's IP address
        self.dns_server_add = ""  # DNS server IP address
        self.subnet_mask = None
        self.router = None
