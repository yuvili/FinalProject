from socket import *  # For socket programming
import threading  # Create a new thread to handle the client request
from src.backend.HTTP_Docs.HTTP_Servers import image

IMAGE_SERVER_IP = "127.0.0.1"  # Server ip
IMAGE_SERVER_PORT = 20630  # Server port
BUFFER_SIZE = 1024  # Maximum amount of data (bytes) that can be received at once
packets = []

our_image = image.image_in_bytes

def client_handler(client_socket: socket, client_address: tuple[str, int]):
    """
    Function which handles client requests
    :param client_socket: client's socket
    :param client_address: client IP address and port
    """
    while True:  # Server loop
        if client_socket.fileno() == -1:  # Check if socket are closed if so returns -1
            print("\n")
            print(f"Listening on {IMAGE_SERVER_IP}:{IMAGE_SERVER_PORT} ")
            break

        try:
            data = client_socket.recv(BUFFER_SIZE)  # Receive data from the client
            # if not data:  # If there is no more data to receive, break out of the loop
            #     print(f"Listening on {SERVER_IP}:{SERVER_PORT}")
            #     break

            response_status = data.split(b"\r\n")[0]
            print(response_status)

            if response_status == b"GET /imgs/OurImage.png HTTP/1.1":  # If its a PNG file request
                print(f'GET /OurImage.png HTTP/1.1 request from {client_address[0]}:{client_address[1]}')

                response = b"HTTP/1.1 200 OK (JPEG JFIF image)\r\n" \
                           b"Content-Type: text/html\r\n" \
                           b"Connection: keep-alive\r\n\r\n"

                client_socket.sendall(response)  # Send response to the client

                try:
                    with open("OurImage.png", "rb") as f:  # Open file
                        while True:
                            data = f.read(BUFFER_SIZE)  # Read 1024 bytes (BUFFER_SIZE) from the file
                            if not data:  # If there is no more data to read, break out of the loop
                                break

                            client_socket.sendall(data)  # Send the data over the socket

                except FileNotFoundError:
                    print("Error: OurImage.png file not found.")

                except Exception as e:
                    print(f"Error occurred: {e}")

                print(f'Send "OurImage.png" file to {client_address[0]}:{client_address[1]} ')
                client_socket.close()

            else:
                response = b"HTTP/1.1 400 Bad Request\r\n" \
                           b"Content-Type: text/html\r\n" \
                           b"Connection: keep-alive\r\n\r\n"

                client_socket.sendall(response)  # Send response to the client
                print("Error: Bad Request")

        except Exception as e:
            print(f"Unexpected server error: {e}")

def start_server():
    try:
        filename1 = "OurImage.png"
        with open(filename1, 'wb') as f:  # Create new html file
            try:
                f.write(our_image)  # Write all received bytes to the html file
            except Exception as e:
                print(f"Error receiving response: {e}")
            finally:
                f.close()  # Close html file

    except FileNotFoundError:
        print("Error: index.html file not found.")
    except Exception as e:
        print(f"Error occurred: {e}")

    # AF_INET is the address family for IPv4
    # SOCK_STREAM is the socket type for TCP
    # 'with'  closes the socket when the block is exited
    with socket(AF_INET, SOCK_STREAM) as server_socket:  # Create socket
        # "setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)" prevent OSError: [Errno 98] Address already in use
        # The "SO_REUSEADDR" flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Binding the Server to a specific IP address and a PORT number
        server_socket.bind((IMAGE_SERVER_IP, IMAGE_SERVER_PORT))

        # Setting the server to start listening for incoming packets
        # Server only handles one connection at a given time
        # We didn't send any value to the "listen" parameter so a  default value is chosen (set to 0).
        server_socket.listen()

        threads = []
        print(f"Listening on {IMAGE_SERVER_IP}:{IMAGE_SERVER_PORT}")

        while True:
            try:
                # Establish connection with client
                client_socket, address = server_socket.accept()  # Accept a connection
                print(f'Connection established with client {address[0]}:{address[1]}')

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