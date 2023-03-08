import threading
from time import sleep
from tkinter import *
from tkinter.ttk import Labelframe

from DHCP_Docs import dhcp_server
from GUI import Operations


class MainGui:

    def __init__(self):
        # Creating a new window and configurations
        self.window = Tk()
        self.window.title("Final Project")
        self.window.minsize(width=500, height=300)
        self.window.resizable(width=False, height=False)
        self.operator = Operations.Operator()
        self.build_main_frame()
        self.operator.set_window(self.window)
        self.window.mainloop()

    def update_dhcp_screen(self, dhcp_screen):
        dhcp_screen.destroy()
        dhcp_screen.update()
        self.dhcp_op()

    def dhcp_client_request(self, gen_ip_screen, dhcp_screen):
        ack_or_nak = self.operator.dhcp_request()
        self.clear_screen(gen_ip_screen)
        if ack_or_nak:
            ack_label = Label(gen_ip_screen, text=f"Your request is approved!", foreground="green")
            ack_label.pack()
        else:
            ack_label = Label(gen_ip_screen, text=f"Your request is denied!", foreground="red")
            ack_label.pack()

        approve_button = Button(gen_ip_screen, text="OK", width=9, height=1,
                                command=lambda: self.update_dhcp_screen(dhcp_screen))
        approve_button.place(relx=0.5, rely=0.4, anchor=CENTER)

    def dhcp_client_decline(self, gen_ip_screen):
        self.operator.dhcp_decline()
        gen_ip_screen.destroy()
        gen_ip_screen.update()

    def dhcp_generateIP_frame(self, dhcp_screen):
        gen_ip_screen = Toplevel(dhcp_screen)
        gen_ip_screen.title("Generate IP address")
        gen_ip_screen.geometry("300x200")

        offered_ip = self.operator.dhcp_generate_ip()

        approve_button = Button(gen_ip_screen, text="Approve", width=9, height=1,
                                command=lambda: self.dhcp_client_request(gen_ip_screen, dhcp_screen))
        approve_button.place(relx=0.3, rely=0.4, anchor=CENTER)

        decline_button = Button(gen_ip_screen, text="Decline", width=9, height=1,
                                command=lambda: self.dhcp_client_decline(gen_ip_screen))
        decline_button.place(relx=0.7, rely=0.4, anchor=CENTER)

        offered_ip_label = Label(gen_ip_screen, text=f"You got the IP: {offered_ip}")
        offered_ip_label.pack()

    def dhcp_client_release(self, dhcp_screen):
        self.operator.dhcp_client.release()

        release_screen = Toplevel(dhcp_screen)
        release_screen.title("Release IP Address")
        release_screen.geometry("300x250")

        Label(release_screen, text=f"Done", foreground="green").pack()
        approve_button = Button(release_screen, text="OK", width=9, height=1,
                                command=lambda: self.update_dhcp_screen(dhcp_screen))
        approve_button.place(relx=0.5, rely=0.4, anchor=CENTER)

    def dhcp_op(self):
        dhcp_screen = Toplevel(self.window)
        dhcp_screen.title("DHCP")
        dhcp_screen.geometry("200x200")

        generate_button = Button(dhcp_screen, text="Generate IP", width=10, height=1,
               command=lambda: self.dhcp_generateIP_frame(dhcp_screen))

        if self.operator.dhcp_client.ip_add != "0.0.0.0":
            generate_button["state"] = "disabled"
        generate_button.place(relx=0.5, rely=0.3, anchor="center")

        release_button = Button(dhcp_screen, text="Release IP", width=10, height=1,
               command=lambda: self.dhcp_client_release(dhcp_screen))
        if self.operator.dhcp_client.ip_add == "0.0.0.0":
            release_button["state"] = "disabled"
        release_button.place(relx=0.5, rely=0.45, anchor="center")

    def dns_op(self):
        if self.operator.dhcp_client.ip_add == "0.0.0.0":
            error_label = Label(self.window, text='Please claim an IP address first' , font=("Helvetica", 15), foreground="red")
            error_label.pack()
    def build_main_frame(self):
        top_label = Label(self.window, text='Main Menu', font=("Helvetica", 25))
        top_label.pack()

        dhcp_button = Button(self.window, text="DHCP Options", width=10, command=self.dhcp_op)
        dhcp_button.pack(pady=10)

        dns_button = Button(self.window, text="DNS Options", width=10,
                                          command=self.dhcp_op)
        dns_button.pack()

    def clear_screen(self, screen):
        for widgets in screen.winfo_children():
            widgets.destroy()


if __name__ == '__main__':
    thread = threading.Thread(target=dhcp_server.start_server)
    thread.start()
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

