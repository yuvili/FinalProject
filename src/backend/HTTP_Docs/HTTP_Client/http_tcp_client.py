import os
import webbrowser
from socket import *  # For socket programming

# GLOBAL VARIABLES:
SERVER_IP = "127.0.0.1"  # server ip
SERVER_PORT = 30965  # server port
BUFFER_SIZE = 1024  # Maximum amount of data (bytes) that can be received at once

def create_html_file_request():
    """
    Creates a http file request packet
    """
    html_file_request = b"GET / HTTP/1.1\r\n" \
                        b"Host: 127:0:0:1\r\n" \
                        b"Accept: text/html,application/xhtml+xml\r\n" \
                        b"Connection: keep-alive\r\n\r\n"
    return html_file_request

def send_html_file_request(client_socket: socket, server_address: tuple[str, int]):
    """
    "send_http_file_request" send http file request and receive response
    1. if server accept to send html file the client will receive it and write it into a new html file
    2. if server denied request for some reason the client send http file request again at the beginning we check which server the client is currently connected because when the client connect
    with the image_server he already has the html file, and he needs only the png image
    :param client_socket: client's socket
    :param server_address: server's IP address and port
    """

    if server_address[1] == SERVER_PORT:  # Check which server the client is currently connected to
        new_packet = create_html_file_request()  # Create a http file request packet
        client_socket.sendall(new_packet)  # Send the request to the server
        print(f'HTTP Client send HTML file request to {server_address[0]}:{server_address[1]}')

        try:
            data = client_socket.recv(BUFFER_SIZE)  # Receive data from socket

            response_status = data.split(b"\r\n")[0]
            if response_status == b"HTTP/1.1 200 OK (text/html)":
                html_file = data.split(b"\r\n\r\n")[1]
                filename1 = "new_html.html"
                with open(filename1, 'wb') as f:  # Create new html file
                    try:
                        f.write(html_file)  # Write all received bytes to the html file
                    except Exception as e:
                        print(f"Error receiving response: {e}")
                    finally:
                        f.close()  # Close html file
                        url = 'file://' + os.path.realpath(filename1)
                        webbrowser.open_new(url)
                        send_image_request(client_socket, server_address)  # Ask to receive the image
            else:
                send_html_file_request(client_socket, server_address)  # If server denied request - try again

        except FileNotFoundError:
            print("Error: index.html file not found.")
        except Exception as e:
            print(f"Error occurred: {e}")

    else:
        send_image_request(client_socket, server_address)  # Ask to receive the image

def create_image_request():
    """
    Creates a png image file request
    :return: image file request
    """
    image_file_request = b"GET /imgs/OurImage.png HTTP/1.1\r\n" \
                         b"Host: 127:0:0:1\r\n" \
                         b"Accept: image/webp,*/*\r\n" \
                         b"Connection: keep-alive\r\n\r\n"
    return image_file_request

def send_image_request(client_socket: socket, server_address: tuple[str, int]):
    """
    "send_image_request" send png file request and receive response
    1. if server accept to send png file the client will receive it and write it into a new png file
    2. if server denied request for some reason the client send png file request again
    :param client_socket: client's socket
    :param server_address: server's IP address and port
    """
    packet = create_image_request()  # Creates a png image file request packet
    client_socket.sendall(packet)  # Send the request to the server
    print(f'HTTP Client send JPEG image file request to {server_address[0]}:{server_address[1]}')
    try:
        received_image = b''
        data = client_socket.recv(BUFFER_SIZE)  # Receive data from socket
        response_status = data.split(b"\r\n")[0]
        if response_status == b"HTTP/1.1 200 OK (JPEG JFIF image)":
            while True:  # As long as data keeps coming from the socket
                data = client_socket.recv(BUFFER_SIZE)  # Receive data from socket
                if not data:
                    break
                else:
                    received_image += data  # Add data to received bytes

            client_socket.close()
            image_file = received_image
            filename2 = "OurImage.png"
            with open(filename2, 'wb') as f:  # Create new html file
                try:
                    f.write(image_file)  # Write all received bytes to the image file
                except Exception as e:
                    print(f"Error receiving response: {e}")
                finally:
                    f.close()  # Close html file

        elif response_status == b"HTTP/1.1 301 Moved Permanently":
            address = data.split(b"\r\n\r\n")[1]
            new_ip = (address.split(b":")[0]).decode()
            new_port = int((address.split(b":")[1]).decode())
            print(new_port)
            print("--------------------------------")
            print(f'Redirect to {new_ip}:{new_port}')
            print("--------------------------------")
            # time.sleep(10)
            http_request((new_ip, new_port))

        else:
            send_image_request(client_socket, server_address)  # Ask to receive the image

    except FileNotFoundError:
        print("Error: index.html file not found.")
    except Exception as e:
        print(f"Error occurred: {e}")


def http_request(server_address: tuple[str, int]):
    """
    Create a http request that contain html request and png request
    :param server_address: server's IP address and port
    """
    with socket(AF_INET, SOCK_STREAM) as client_socket:  # Create socket
        client_socket.connect(server_address)  # Connect to server address and port
        print(f'HTTP Client connection established with {server_address[0]}:{server_address[1]}')

        try:
            send_html_file_request(client_socket, server_address)  # Creates a http file request
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

def start_client():
    http_request((SERVER_IP, SERVER_PORT))  # "Start" client

if __name__ == "__main__":
    http_request((SERVER_IP, SERVER_PORT))  # "Start" client