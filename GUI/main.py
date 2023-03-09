import threading
from tkinter import *
from customtkinter import *
from DHCP_Docs import dhcp_server
from DNS_Docs import dns_server
from GUI import Operations


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

        self.mid_frame = CTkFrame(self.window, width=500,)
        self.op_frame = CTkFrame(self.window, width=500)

        self.main_frame()
        self.operator.set_window(self.window)
        self.window.mainloop()

    def update_dhcp_screen(self):
        self.clear_screen(self.op_frame)

        dhcp_actions = CTkLabel(self.op_frame, text="DHCP Actions", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=20, pady=(60, 10))

        generate_button = CTkButton(self.op_frame, text="Generate IP Address", command=self.dhcp_generateIP_frame)
        if self.operator.dhcp_client.ip_add != "0.0.0.0":
            generate_button.configure(state="disabled")
        generate_button.grid(row=1, column=0, padx=(60, 60), pady=10)

        release_button = CTkButton(self.op_frame, text="Release IP", command=self.dhcp_client_release)
        if self.operator.dhcp_client.ip_add == "0.0.0.0":
            release_button.configure(state="disabled")
        release_button.grid(row=2, column=0, padx=(60, 60), pady=10)

    def dhcp_client_request(self):
        ack_or_nak = self.operator.dhcp_request()
        self.clear_screen(self.op_frame)
        if ack_or_nak:
            ack_label = CTkLabel(self.op_frame, text=f"Your request is approved!", fg_color="green")
            ack_label.grid(row=0, column=0, padx=(60,60), pady=60)
        else:
            ack_label = CTkLabel(self.op_frame, text=f"Your request is denied!", fg_color="red")
            ack_label.grid(row=0, column=0, padx=(60,60), pady=60)

        approve_button = CTkButton(self.op_frame, text="OK",
                                command=self.update_dhcp_screen)
        approve_button.grid(row=1, column=0, padx=(60,60), pady=10)

    def dhcp_client_decline(self):
        self.operator.dhcp_decline()
        self.update_dhcp_screen()

    def dhcp_generateIP_frame(self):
        # gen_ip_screen = CTkLabel(self.mid_frame, text="")
        # gen_ip_screen.title("Generate IP address")
        # gen_ip_screen.geometry("300x200")
        self.clear_screen(self.op_frame)
        # self.opp_frame()

        dhcp_actions = CTkLabel(self.op_frame, text="Generate IP address", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=40, pady=(60, 10))

        offered_ip = self.operator.dhcp_generate_ip()

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
                                   command=self.update_dhcp_screen)
        approve_button.grid(row=1, column=0, padx=(60, 60), pady=10)

        # release_screen = CTkToplevel(dhcp_screen)
        # release_screen.title("Release IP Address")
        # release_screen.geometry("300x250")

        # CTkLabel(release_screen, text=f"Done", foreground="green").pack()
        # approve_button = CTkButton(release_screen, text="OK", width=9, height=1,
        #                         command=lambda: self.update_dhcp_screen())
        # approve_button.place(relx=0.5, rely=0.4, anchor=CENTER)

    def dhcp_op(self):
        self.middle_frame()
        self.opp_frame()
        # dhcp_info = CTkLabel(self.mid_frame, text="DHCP Info", font=CTkFont(size=15, weight="bold"))
        # dhcp_info.grid(row=0, column=0, padx=20, pady=(20, 10))

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

        dhcp_actions = CTkLabel(self.op_frame, text="DHCP Actions", font=CTkFont(size=15, weight="bold"))
        dhcp_actions.grid(row=0, column=0, padx=20, pady=(60, 10))

        #TODO: small explenation on methood
        # dhcp_screen = CTkToplevel(self.window)
        # dhcp_screen.title("DHCP")
        # dhcp_screen.geometry("200x200")

        generate_button = CTkButton(self.op_frame, text="Generate IP Address", command= self.dhcp_generateIP_frame)
        if self.operator.dhcp_client.ip_add != "0.0.0.0":
            generate_button.configure(state= "disabled")
        generate_button.grid(row=1, column=0, padx=(60,60), pady=10)

        release_button = CTkButton(self.op_frame, text="Release IP", command=self.dhcp_client_release)
        if self.operator.dhcp_client.ip_add == "0.0.0.0":
            release_button.configure(state= "disabled")
        release_button.grid(row=2, column=0, padx=(60,60), pady=10)

    def get_ip(self, hostname_entry, dns_screen):
        hostname = hostname_entry.get()
        ip_answer = self.operator.dns_query(hostname)

        self.clear_screen(dns_screen)
        head_label = CTkLabel(dns_screen, text=f'The IP of host {hostname} is: {ip_answer}', font=("Helvetica", 15))
        head_label.pack(pady=10)

    def dns_op(self):
        if self.operator.dhcp_client.ip_add == "0.0.0.0":
            error_label = CTkLabel(self.window, text='Please claim an IP address first' , font=("Helvetica", 15), foreground="red")
            error_label.pack()
            return

        dns_screen = CTkToplevel(self.window)
        dns_screen.title("DNS Query")
        dns_screen.geometry("400x200")

        head_label = CTkLabel(dns_screen, text='Please enter your hostname address:', font=("Helvetica", 15))
        head_label.pack(pady=10)

        hostname_entry = CTkEntry(dns_screen, width=300)
        hostname_entry.pack(pady=10)

        generate_button = CTkButton(dns_screen, text="Search", width=10, height=1,
                                 command=lambda: self.get_ip(hostname_entry, dns_screen))
        generate_button.pack()

    def main_frame(self):
        top_label = CTkLabel(self.main_menu_frame, text='Main Menu', font=("Tahoma", 25))
        top_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        dhcp_button = CTkButton(self.main_menu_frame, text="DHCP Options", command=self.dhcp_op)
        dhcp_button.grid(row=1, column=0, padx=20, pady=10)

        dns_button = CTkButton(self.main_menu_frame, text="DNS Options", command=self.dns_op)
        dns_button.grid(row=2, column=0, padx=20, pady=10)

        http_button = CTkButton(self.main_menu_frame, text="HTTP Application", command=self.dns_op)
        http_button.grid(row=3, column=0, padx=20, pady=10)

        CTkLabel(self.main_menu_frame, text='').grid(row=4, column=0, padx=20, pady=10)
        CTkLabel(self.main_menu_frame, text='').grid(row=5, column=0, padx=20, pady=10)
        CTkLabel(self.main_menu_frame, text='').grid(row=6, column=0, padx=20, pady=10)

        client_details_button = CTkButton(self.main_menu_frame, text="Client Info", command=self.dns_op)
        client_details_button.grid(row=7, column=0, padx=20, pady=10)

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
    threading.Thread(target=dhcp_server.start_server).start()
    #threading.Thread(target=dns_server.start_server).start()
    gui = MainGui()

#
# frame = Frame(window)
#
# # Labels
# label = Label(window, text="Main Menu", foreground="black", background="white", font=("Helvetica", 25))
# label.pack()


# button = Button(text="DHCP Options", command=self.action, borderless=1, bg="green", fg="white")
# button.place(x=180, y=100)
#
# # Entries
# entry = Entry(width=30)
# # Add some text to begin with
# entry.insert(END, string="Some text to begin with.")
# # Gets text in entry
# print(entry.get())
# entry.pack()
#
# # Text
# text = Text(height=5, width=30)
# # Puts cursor in textbox.
# text.focus()
# # Adds some text to begin with.
# text.insert(END, "Example of multi-line text entry.")
# # Get's current value in textbox at line 1, character 0
# print(text.get("1.0", END))
# text.pack()
#
#
# # Spinbox
# def spinbox_used():
#     # gets the current value in spinbox.
#     print(spinbox.get())
#
#
# spinbox = Spinbox(from_=0, to=10, width=5, command=spinbox_used)
# spinbox.pack()
#
#
# # Scale
# # Called with current scale value.
# def scale_used(value):
#     print(value)
#
#
# scale = Scale(from_=0, to=100, command=scale_used)
# scale.pack()
#
#
# # Checkbutton
# def checkbutton_used():
#     # Prints 1 if On button checked, otherwise 0.
#     print(checked_state.get())
#
#
# # variable to hold on to checked state, 0 is off, 1 is on.
# checked_state = IntVar()
# checkbutton = Checkbutton(text="Is On?", variable=checked_state, command=checkbutton_used)
# checked_state.get()
# checkbutton.pack()
#
#
# # Radiobutton
# def radio_used():
#     print(radio_state.get())
#
#
# # Variable to hold on to which radio button value is checked.
# radio_state = IntVar()
# radiobutton1 = Radiobutton(text="Option1", value=1, variable=radio_state, command=radio_used)
# radiobutton2 = Radiobutton(text="Option2", value=2, variable=radio_state, command=radio_used)
# radiobutton1.pack()
# radiobutton2.pack()
#
#
# # Listbox
# def listbox_used(event):
#     # Gets current selection from listbox
#     print(listbox.get(listbox.curselection()))
#
#
# listbox = Listbox(height=4)
# fruits = ["Apple", "Pear", "Orange", "Banana"]
# for item in fruits:
#     listbox.insert(fruits.index(item), item)
# listbox.bind("<<ListboxSelect>>", listbox_used)
# listbox.pack()

