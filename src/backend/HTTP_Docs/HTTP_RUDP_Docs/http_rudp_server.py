import pickle
from socket import *
import time
from rudp_packet import Packet
from rudp_flow_control import FlowControl
from rudp_congestion_control import CongestionControl

# GLOBAL VARIABLES:
SERVER_IP = "127.0.0.1"
SERVER_PORT = 30965
IMAGE_SERVER_IP = "127.0.0.1"
IMAGE_SERVER_PORT = 30966
BUFFER_SIZE = 65536  # The buffer size is the maximum amount of data that can be received at once
FRAGMENT_SIZE = 1000  # In bytes
WINDOW_SIZE = 10  # In frames
TIMEOUT = 10  # Default time out for packets (in seconds)
FILE_HTML_NAME = "new_html.html"
FILE_IMAGE_NAME = "OurImage.png"
client_list = []  # List of connected UDP clients
packets = []


class WindowControl:
    def __init__(self, window_size):
        self.window_size = window_size
        self.packets = (None, ) * window_size
        self.next_sequence_number = 0
        self.base = 0

    def add_packet(self, packet):
        if self.next_sequence_number < self.base + self.window_size:
            self.packets[self.next_sequence_number % self.window_size] = packet
            self.next_sequence_number += 1
            return True
        else:
            return False

    def get_next_packet(self):
        if self.base < self.next_sequence_number:
            packet = self.packets[self.base % self.window_size]
            self.base += 1
            return packet
        else:
            return None


def divide_into_packets(file_name: str):
    if file_name == "new_html.html":
        try:
            with open('new_html.html', 'rb') as file:  # Open file
                data = file.read()  # Read from file

                # divide data into packets
                while data > 0:
                    packet_data = data[:BUFFER_SIZE]  # 1024 bytes (BUFFER_SIZE) per packet
                    data = data[BUFFER_SIZE:]
                    packet = Packet(packet_data, (SERVER_IP, SERVER_PORT))
                    self.ClientWindowControl.add_packet(packet)
                    self.sequence_number += 1
                    packets.append(packet)

        except FileNotFoundError:
            print("Error: index.html file not found.")

        except Exception as e:
            print(f"Error occurred: {e}")


def send_file(file_type: str, server_sock: socket, client_address: tuple[str, int]):
    if file_type == "html":
        divide_into_packets("new_html.html")
        try:
            send(server_sock, client_address)

        except Exception as e:
            print(f"Error occurred: {e}")

    else:
        print("Error: This file type not exist.")


# Redirect the client to the image server after receiving his request for image
def redirect(server_socket: socket, client_address: tuple[str, int]):
    print(f'Redirect {client_address[0]}:{client_address[1]} to {IMAGE_SERVER_IP}:{IMAGE_SERVER_PORT}'
          f' for downloading OurImage.png file')
    # Create packet with the image server address
    new_packet = Packet("Redirect", (IMAGE_SERVER_IP, IMAGE_SERVER_PORT))
    obj_bytes = pickle.dumps(new_packet)  # Packet to bytes
    server_socket.sendto(obj_bytes, client_address)  # Send the data over the socket


# Function which handles client requests
def client_handler(server_socket: socket, response: Packet, client_address: tuple[str, int]):
    try:
        if response.data == "Connection_Request":  # Establish connection
            print(f'GET connection request from {client_address[0]}:{client_address[1]}')
            client_list.append(client_address)  # Add client to list (for authorisation)
            new_packet = Packet("ACK", (SERVER_IP, SERVER_PORT))  # Send ACK to confirm connection
            obj_bytes = pickle.dumps(new_packet)  # Packet to bytes
            server_socket.sendto(obj_bytes, client_address)  # Send the data over the socket
            print(f'Connect with {client_addr[0]}:{client_addr[1]}')

        # Authentication protocol to prevent unauthorized clients receiving the files
        elif response.data == "Authentication_Request":
            print(f'GET authentication request from {client_address[0]}:{client_address[1]}')
            if client_address in client_list:
                new_packet = Packet("ACK", (SERVER_IP, SERVER_PORT))  # Send ACK to confirm authentication
                obj_bytes = pickle.dumps(new_packet)  # Packet to bytes
                server_socket.sendto(obj_bytes, client_address)  # Send the data over the socket
                print(f'Authentication with {client_addr[0]}:{client_addr[1]} confirmed')
            else:
                new_packet = Packet("NACK", (SERVER_IP, SERVER_PORT))  # Send NACK to denied authentication
                obj_bytes = pickle.dumps(new_packet)  # Packet to bytes
                server_socket.sendto(obj_bytes, client_address)  # Send the data over the socket
                print(f'Authentication with {client_addr[0]}:{client_addr[1]} denied')

        elif response.data == "GET /new_html.html HTTP/1.1":  # If its a HTML file request
            print(f'GET /new_html.html HTTP/1.1 request from {client_address[0]}:{client_address[1]}')
            new_packet = Packet("HTTP / 1.1 200 OK , Type: text/html",
                                (SERVER_IP, SERVER_PORT))  # Confirm request
            obj_bytes = pickle.dumps(new_packet)  # Packet to bytes
            server_socket.sendto(obj_bytes, client_address)  # Send the data over the socket
            send_file("html", server_socket, client_address)  # Start to send the HTML file
            print(f'Send "new_html.html" file to {client_address[0]}:{client_address[1]}')

        elif response.data == "GET /OurImage.png HTTP/1.1":  # If its a PNG file request
            print(f'GET /OurImage.png HTTP/1.1 request from {client_address[0]}:{client_address[1]}')
            redirect(server_socket, client_address)  # Redirect the client to the image server

        else:
            new_packet = Packet("Request denied", (SERVER_IP, SERVER_PORT))  # Denied request
            obj_bytes = pickle.dumps(new_packet)  # Packet to bytes
            server_socket.sendto(obj_bytes, client_address)  # Send the data over the socket
            print("Error: This file type not exist.")

    except Exception as e:
        print(f"Unexpected server error: {e}")


def start_server():
    window_Control = Window_Control(window_size)
    flow_control = FlowControl(window_size)
    congestion_control = CongestionControl
    sequence_number = 0
    timeout = TIMEOUT  # timeout in seconds
    image_in_cash = false

    # AF_INET is the address family for IPv4
    # SOCK_DGRAM is the socket type for UDP
    # 'with'  closes the socket when the block is exited
    with socket(AF_INET, SOCK_DGRAM) as RUDP_server_socket:  # Create socket
        # "setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)" prevent OSError: [Errno 98] Address already in use
        # The "SO_REUSEADDR" flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.
        RUDP_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # Binding the Server to a specific IP address and a PORT number
        RUDP_server_socket.bind((SERVER_IP, SERVER_PORT))

        threads = []
        while True:
            print(f"Server {SERVER_IP}:{SERVER_PORT} is ON")
            try:
                data, client_address = RUDP_server_socket.recvfrom(FRAGMENT_SIZE)
                response_packet = pickle.loads(data)  # Bytes to packet
                # Create a new thread to handle the client request
                thread = threading.Thread(target=client_handler,
                                          args=(RUDP_server_socket, response_packet, client_address))
                thread.start()
                threads.append(thread)
            except KeyboardInterrupt:
                print("Shutting down...")
                break

        for thread in threads:  # Wait for all threads to finish
            thread.join()


if __name__ == "__main__":
    start_server()
