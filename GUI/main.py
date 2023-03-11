import threading

from customtkinter import *
# from DHCP_Docs import dhcp_server
import Operations
from DHCP_Docs import server


class MainGui:

    def __init__(self):
        # Creating a new window and configurations
        self.window = CTk()
        self.window.title("Final Project")
        self.window.geometry(f"{800}x{400}")
        self.window.resizable(width=False, height=False)
        self.operator = Operations.Operator()

        self.main_menu_frame = CTkFrame(self.window, width=500, corner_radius=0)
        self.main_menu_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.main_menu_frame.grid_rowconfigure(4, weight=1)

        self.top_label = CTkLabel(self.main_menu_frame, text='Main Menu', font=("Tahoma", 25))
        self.top_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dhcp_button = CTkButton(self.main_menu_frame, text="DHCP Options", command=self.dhcp_op)
        self.dhcp_button.grid(row=1, column=0, padx=20, pady=10)

        self.dns_button = CTkButton(self.main_menu_frame, text="DNS Options", command=self.dns_screen)
        self.dns_button.grid(row=2, column=0, padx=20, pady=10)
        if self.operator.dhcp_client.ip_address == "0.0.0.0":
            self.dns_button.configure(state="disabled")

        self.http_button = CTkButton(self.main_menu_frame, text="HTTP Application", command=self.dns_screen)
        self.http_button.grid(row=3, column=0, padx=20, pady=10)

        CTkLabel(self.main_menu_frame, text='').grid(row=4, column=0, padx=20, pady=10)
        CTkLabel(self.main_menu_frame, text='').grid(row=5, column=0, padx=20, pady=10)
        CTkLabel(self.main_menu_frame, text='').grid(row=6, column=0, padx=20, pady=10)

        self.client_details_button = CTkButton(self.main_menu_frame, text="Client Info", command=self.dns_screen)
        self.client_details_button.grid(row=7, column=0, padx=20, pady=10)

        self.mid_frame = CTkFrame(self.window, width=500,)
        self.op_frame = CTkFrame(self.window, width=500)

        self.main_frame()
        self.operator.set_window(self.window)
        self.window.mainloop()

    def update_dns_button(self):
        self.dns_button.destroy()
        self.dns_button = CTkButton(self.main_menu_frame, text="DNS Options", command=self.dns_screen)
        self.dns_button.grid(row=2, column=0, padx=20, pady=10)
        if self.operator.dhcp_client.ip_address == "0.0.0.0":
            self.dns_button.configure(state="disabled")

    def dhcp_client_request(self):
        ack_or_nak = self.operator.dhcp_request()
        self.clear_screen(self.op_frame)
        if ack_or_nak == "True":
            ack_label = CTkLabel(self.op_frame, text=f"Your request is approved!", fg_color="green")
            ack_label.grid(row=0, column=0, padx=(60,60), pady=60)
            self.update_dns_button()

            approve_button = CTkButton(self.op_frame, text="OK",
                                       command=self.dhcp_screen)
            approve_button.grid(row=1, column=0, padx=(60, 60), pady=10)

        elif ack_or_nak == "False":
            ack_label = CTkLabel(self.op_frame, text=f"Your request is denied!", fg_color="red")
            ack_label.grid(row=0, column=0, padx=(60,60), pady=60)

            approve_button = CTkButton(self.op_frame, text="OK",
                                       command=self.dhcp_screen)
            approve_button.grid(row=1, column=0, padx=(60, 60), pady=10)

        elif ack_or_nak == "error":
            self.dhcp_error_screen()

    def dhcp_client_decline(self):
        self.operator.dhcp_decline()
        self.dhcp_screen()

    def dhcp_error_screen(self):
        self.clear_screen(self.op_frame)

        dhcp_actions = CTkLabel(self.op_frame, text="Something wend wrong...", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=40, pady=(60, 10))

        approve_button = CTkButton(self.op_frame, text="Retry",
                                   command=self.dhcp_generateIP_frame)
        approve_button.grid(row=1, column=0, padx=(60, 60), pady=10)

    def dhcp_generateIP_frame(self):
        self.clear_screen(self.op_frame)

        dhcp_actions = CTkLabel(self.op_frame, text="Generate IP address", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=40, pady=(60, 10))

        offered_ip = self.operator.dhcp_generate_ip()
        if offered_ip == "timeout error":
            self.dhcp_error_screen()


        offered_ip_label = CTkLabel(self.op_frame, text=f"You got the IP: {offered_ip}")
        offered_ip_label.grid(row=1, column=0, padx=10, pady=(20, 10))

        approve_button = CTkButton(self.op_frame, text="Approve",
                                command=self.dhcp_client_request)
        approve_button.grid(row=2, column=0, padx=(60,60), pady=10)

        decline_button = CTkButton(self.op_frame, text="Decline",
                                command=self.dhcp_client_decline)
        decline_button.grid(row=3, column=0, padx=(60,60), pady=10)

    def dhcp_client_release(self):
        self.operator.dhcp_client.release()
        self.clear_screen(self.op_frame)

        ack_label = CTkLabel(self.op_frame, text="Your IP address was released!")
        ack_label.grid(row=0, column=0, padx=(20,20), pady=60)

        approve_button = CTkButton(self.op_frame, text="OK",
                                   command=self.dhcp_screen)
        approve_button.grid(row=1, column=0, padx=(60, 60), pady=10)

        self.update_dns_button()

    def dhcp_screen(self):
        self.clear_screen(self.op_frame)

        dhcp_actions = CTkLabel(self.op_frame, text="DHCP Actions", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=20, pady=(60, 10))

        generate_button = CTkButton(self.op_frame, text="Generate IP Address", command=self.dhcp_generateIP_frame)
        if self.operator.dhcp_client.ip_address != "0.0.0.0":
            generate_button.configure(state="disabled")
        generate_button.grid(row=1, column=0, padx=(60, 60), pady=10)

        release_button = CTkButton(self.op_frame, text="Release IP", command=self.dhcp_client_release)
        if self.operator.dhcp_client.ip_address == "0.0.0.0":
            release_button.configure(state="disabled")
        release_button.grid(row=2, column=0, padx=(60, 60), pady=10)

    def dhcp_op(self):
        self.clear_screen(self.mid_frame)

        dhcp_textbox = CTkTextbox(self.mid_frame, width=250, height=380)
        dhcp_textbox.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        dhcp_info_text = 'DHCP\n\nIn this page you will have an option to \ngenerate yourself an IP ' \
                         'address, in \ncase you don`t have on, or release \nyour current IP address. ' \
                         '\nBy default, when starting the program your IP address is "0.0.0.0", so please start'\
                         ' with generating an address.\n\n' \
                         'The "Generate IP Address" option is \navailable only in case when your IP \nis "0.0.0.0".' \
                         '\nIn case when you have a different IP \naddress and you wish to replace it, \nplease release your IP with "Release \nIP"' \
                         ' action first.'
        dhcp_textbox.insert("0.0", dhcp_info_text)

        self.dhcp_screen()

    def get_ip(self, hostname_entry):
        hostname = hostname_entry.get()
        ip_answer = self.operator.dns_query(hostname)

        self.clear_screen(self.op_frame)
        head_label = CTkLabel(self.op_frame, text=f'The IP of host \n{hostname} is: \n{ip_answer}', font=("Helvetica", 15))
        head_label.grid(row=0, column=0, padx=(60,60), pady=110)

        approve_button = CTkButton(self.op_frame, text="New Query",
                                   command=self.dns_control_screen)
        approve_button.grid(row=2, column=0, padx=(60, 60), pady=10)

    def dns_control_screen(self):
        self.clear_screen(self.op_frame)

        dhcp_actions = CTkLabel(self.op_frame, text="Please enter your hostname address:", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=20, pady=(60, 10))

        hostname_entry = CTkEntry(self.op_frame, width=300)
        hostname_entry.grid(row=1, pady=10)

        approve_button = CTkButton(self.op_frame, text="Search",
                                   command=lambda: self.get_ip(hostname_entry))
        approve_button.grid(row=2, column=0, padx=(60, 60), pady=10)

    def dns_screen(self):
        self.clear_screen(self.mid_frame)

        dhcp_textbox = CTkTextbox(self.mid_frame, width=250, height=380)
        dhcp_textbox.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        dhcp_info_text = 'DNS\n\nIn this page you will have an option to \nmake a DNS query ' \
                         'where you will \nprovide a hostname and as a result, \nyou will get the corresponding IP ' \
                         '\naddress.\n\n'\
                         'Notice that this option won`t be \navailable if you haven`t generated \nyourself an IP address' \
                         'yet through the DHCP option menu.' \
                         '\n\nWhen making a DNS query, please fill out an address in the form of:' \
                         '\nwww.name.com/org/co.il ect...'

        dhcp_textbox.insert("0.0", dhcp_info_text)

        self.dns_control_screen()

    def html_actions(self):
        self.clear_screen(self.op_frame)

        dhcp_actions = CTkLabel(self.op_frame, text="DHCP Actions", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=20, pady=(60, 10))

        generate_button = CTkButton(self.op_frame, text="Get Image", command=self.operator.get_image)
        generate_button.grid(row=1, column=0, padx=(60, 60), pady=10)

    def html_screen(self):
        self.clear_screen(self.mid_frame)

        dhcp_textbox = CTkTextbox(self.mid_frame, width=250, height=380)
        dhcp_textbox.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        dhcp_info_text = 'DHCP\n\nIn this page you will have an option to \ngenerate yourself an IP ' \
                         'address, in \ncase you don`t have on, or release \nyour current IP address. ' \
                         '\nBy default, when starting the program your IP address is "0.0.0.0", so please start' \
                         ' with generating an address.\n\n' \
                         'The "Generate IP Address" option is \navailable only in case when your IP \nis "0.0.0.0".' \
                         '\nIn case when you have a different IP \naddress and you wish to replace it, \nplease release your IP with "Release \nIP"' \
                         ' action first.'
        dhcp_textbox.insert("0.0", dhcp_info_text)

        self.html_actions()

    def client_info_details(self):
        self.clear_screen(self.op_frame)

        client = self.operator.dhcp_client

        client_details = {
            "Physical Address": client.mac_address,
            "IPv4": client.ip_address,
            "IPv4 Subnet Mask": client.subnet_mask,
            "Lease Obtain": client.lease_obtain,
            "Lease Expires": client.lease_expires,
            "IPv4 Default Gateway": client.router,
            "IPv4 DHCP Server": client.dhcp_server_ip,
            "IPv4 DNS Server": client.dns_server_address
        }
        i=0
        for detail in client_details:
            CTkLabel(self.op_frame, text=f"{detail}: ",
                                font=CTkFont(size=15, weight="bold"), anchor="nw")\
                .grid(row=i, column=0, pady=10)
            CTkLabel(self.op_frame, text=client_details[detail],
                     font=CTkFont(size=15), anchor="nw") \
                .grid(row=i, column=1, pady=10)
            i+=1

    def client_info_screen(self):
        # self.clear_screen(self.mid_frame)
        self.middle_frame()
        self.opp_frame()

        dhcp_textbox = CTkTextbox(self.mid_frame, width=250, height=380)
        dhcp_textbox.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        dhcp_info_text = 'Client Info\n\nThe following information shows the\nclient`s network details, ' \
                         'which are\nbeing updated throughout the\nprogram`s run.' \
                         '\n\nThe Physical Address field is your\ncomputer`s Mac Address.' \
                         '\n\nAt the beginning of the program run\nor when the DHCP RELEASE action\n' \
                         'takes place, the following fields will \nbe empty:\n- "IPv4 Subnet Mask"\n- "Lease Obtain"\n- "Lease Expires"\n- ' \
                         '"IPv4 Default Gateway"\n- "IPv4 DHCP Server"\n- "IPv4 DNS Server"' \
                         '\nThese fields will be empty since they relay on the DHCP IP claiming \nprocedure. '

        dhcp_textbox.insert("0.0", dhcp_info_text)
        self.client_info_details()

    def main_frame(self):
        top_label = CTkLabel(self.main_menu_frame, text='Main Menu', font=("Tahoma", 25))
        top_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        dhcp_button = CTkButton(self.main_menu_frame, text="DHCP Options", command=self.dhcp_op)
        dhcp_button.grid(row=1, column=0, padx=20, pady=10)

        dns_button = CTkButton(self.main_menu_frame, text="DNS Options", command=self.dns_screen)
        dns_button.grid(row=2, column=0, padx=20, pady=10)
        if self.operator.dhcp_client.ip_address == "0.0.0.0":
            dns_button.configure(state="disabled")

        http_button = CTkButton(self.main_menu_frame, text="HTTP Application", command=self.html_screen)
        http_button.grid(row=3, column=0, padx=20, pady=10)

        CTkLabel(self.main_menu_frame, text='').grid(row=4, column=0, padx=20, pady=10)
        CTkLabel(self.main_menu_frame, text='').grid(row=5, column=0, padx=20, pady=10)
        CTkLabel(self.main_menu_frame, text='').grid(row=6, column=0, padx=20, pady=10)

        client_details_button = CTkButton(self.main_menu_frame, text="Client Info", command=self.client_info_screen)
        client_details_button.grid(row=7, column=0, padx=20, pady=10)

        self.middle_frame()
        self.opp_frame()

    def middle_frame(self):
        self.mid_frame.grid(row=0, column=3, padx=(10, 10), pady=(5, 5), sticky="nsew")
        self.mid_frame.grid_rowconfigure(3, weight=1)

    def opp_frame(self):
        self.op_frame.grid(row=0, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew", rowspan=4)
        self.op_frame.grid_rowconfigure(4, weight=1)

    def clear_screen(self, frame):
        for widgets in frame.winfo_children():
            widgets.destroy()


if __name__ == '__main__':
    threading.Thread(target=server.start_server).start()
    # threading.Thread(target=http_tcp_server.start_server).start()
    # threading.Thread(target=http_tcp_image_server.start_server).start()

    gui = MainGui()