from tkinter import *
from tkinter.ttk import Labelframe
from GUI import Operations


class MainGui:

    def __init__(self):
        # Creating a new window and configurations
        self.window = Tk()
        self.window.title("Final Project")
        self.window.minsize(width=500, height=300)
        self.window.config(bg="white")
        self.window.resizable(width=False, height=False)
        self.operator = Operations.Operator()
        self.build_main_frame()
        self.operator.set_window(self.window)
        self.window.mainloop()

    def dhcp_op(self):
        dhcp_screen = Toplevel(self.window)
        dhcp_screen.title("DHCP Operations")
        dhcp_screen.geometry("200x250")

        Label(dhcp_screen, text="").pack()
        Button(dhcp_screen, text="Generate IP", width=10, height=1,
               command=lambda: self.dhcp_generateIP_frame(dhcp_screen)).place(relx=0.5, rely=0.2,
                                                                                            anchor=CENTER)
        Button(dhcp_screen, text="Release IP", width=10, height=1,
               command=lambda: self.operator.dhcp_generate_ip(dhcp_screen)).place(relx=0.5, rely=0.3,
                                                                                  anchor=CENTER)
    def dhcp_generateIP_frame(self, dhcp_screen):
        gen_ip_screen = Toplevel(dhcp_screen)
        gen_ip_screen.title("Generate IP address")
        gen_ip_screen.geometry("300x250")

        self.operator.dhcp_generate_ip(gen_ip_screen)


    def build_main_frame(self):
        top_frame = Labelframe(self.window, text='Main Menu', width=300)
        top_frame.pack(padx=15)

        dhcp_button = Button(top_frame, text="DHCP Options", width=10, command=self.dhcp_op)
        dhcp_button.pack(side='left', padx=5)

        dns_button = Button(top_frame, text="DNS Options", width=10, bg="green", fg="white",
                                          command=self.dhcp_op, state=DISABLED)
        dns_button.pack(side='left', padx=5)


if __name__ == '__main__':
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

