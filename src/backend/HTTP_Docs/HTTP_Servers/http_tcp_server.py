from socket import *  # For socket programming
import threading  # Create a new thread to handle the client request

# GLOBAL VARIABLES:
SERVER_IP = "127.0.0.1"
SERVER_PORT = 30965
IMAGE_SERVER_IP = "127.0.0.1"  # The ip of the image server - that contain the png image file
IMAGE_SERVER_PORT = 20630  # The port of the image server - that contain the png image file
BUFFER_SIZE = 1024  # Maximum amount of data (bytes) that can be received at once
def redirect(client_socket: socket, client_address: tuple[str, int]):
    """
    Redirect the client to the image server after receiving his request for image
    :param client_socket: client's socket
    :param client_address: client's IP address anf port
    """
    print(f'Redirect {client_address[0]}:{client_address[1]} to {IMAGE_SERVER_IP}:{IMAGE_SERVER_PORT}'
          f' for downloading OurImage.png file')
    # Create packet with the image server address
    response = b"HTTP/1.1 301 Moved Permanently\r\n" \
               b"Connection: keep-alive\r\n\r\n" \
               b"Content-Type: text/html\r\n\r\n" \
               b"Location: http://127.0.0.1:20630\r\n"

    client_socket.sendall(response)  # Send the data over the socket
    client_socket.close()

def client_handler(client_socket: socket, client_address: tuple[str, int]):
    """
    Function which handles client requests
    :param client_socket: client's socket
    :param client_address: client's IP address anf port
    """
    while True:  # Server loop
        if client_socket.fileno() == -1:  # Check if socket are closed if so returns -1
            print("\n")
            print(f"HTTP Server listening on {SERVER_IP}:{SERVER_PORT} ")
            break

        try:
            data = client_socket.recv(BUFFER_SIZE)  # Receive data from the client

            response_status = data.split(b"\r\n")[0]
            print(response_status)
            # time.sleep(5)
            if response_status == b"GET / HTTP/1.1":
                print(f'GET / HTTP/1.1 request from {client_address[0]}:{client_address[1]}')
                response = b"POST / HTTP/1.1 200 OK\r\n" \
                           b"Connection: keep-alive\r\n\r\n" \
                           b"Content-Type: text/html\r\n\r\n" \
                           b"<html><title>Final Project</title><body><h1>Final project in the communication networks " \
                           b"course:</h1><p><img src='OurImage.png'></p><h3>Presenters:    <br />Alina zakhozha ID: " \
                           b"323431965    <br />Yuval Shabat   ID: 318516630</h3></body></html> "

                client_socket.sendall(response)  # Send the data over the socket
                print(f'Send "new_html.html" file to {client_address[0]}:{client_address[1]}')

            elif response_status == b"GET /imgs/OurImage.png HTTP/1.1":  # If its a PNG file request
                print(f'GET /OurImage.png HTTP/1.1 request from {client_address[0]}:{client_address[1]}')
                redirect(client_socket, client_address)  # Redirect the client to the image server

            else:
                response = b"POST / HTTP/1.1 400 Bad Request\r\n" \
                           b"Content-Type: text/html\r\n" \
                           b"Connection: keep-alive\r\n\r\n"

                client_socket.sendall(response)  # Send response to the client
                print("Error: Bad Request")

        except Exception as e:
            print(f"Unexpected server error: {e}")

def start_server():
    # AF_INET is the address family for IPv4
    # SOCK_STREAM is the socket type for TCP
    # 'with'  closes the socket when the block is exited
    with socket(AF_INET, SOCK_STREAM) as server_socket:   # Create socket
        # "setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)" prevent OSError: [Errno 98] Address already in use
        # The "SO_REUSEADDR" flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # Binding the Server to a specific IP address and a PORT number
        server_socket.bind((SERVER_IP, SERVER_PORT))
        # Setting the server to start listening for incoming packets
        # Server only handles one connection at a given time
        # We didn't send any value to the "listen" parameter so a  default value is chosen (set to 0).
        server_socket.listen()

        threads = []
        print(f"HTTP Server listening on {SERVER_IP}:{SERVER_PORT} ")

        while True:
            try:
                # Establish connection with client
                client_socket, address = server_socket.accept()  # Accept a connection
                print(f'HTTP Server connection established with client {address[0]}:{address[1]}')

                # Create a new thread to handle the client request
                thread = threading.Thread(target=client_handler, args=(client_socket, address))
                thread.start()
                threads.append(thread)
            except KeyboardInterrupt:
                print("Shutting down...")
                break

        for thread in threads:  # Wait for all threads to finish
            thread.join()


if __name__ == "__main__":
    start_server()