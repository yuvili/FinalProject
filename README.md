# Computer-Networking Course Final Project
>Made by: [Yuval Shabat](https://github.com/yuvili) & [Alina Zahozi](https://github.com/AlinaZahozi)

## How To use
1. Navigate to ``DNS_Docs`` folder using your cd command (pycharm terminal). 
```sh
cd src/backend/DNS_Docs
```

2. Run ```dns_server.py``` with the `sudo` command.
```sh
sudo python3 dns_server.py
```
3. Next, navigate to ``src\frontend`` folder and run ```main.py```

## Introduction
The goal of this project is to develop a system that combines three 
essential servers: a DHCP server, a DNS server, and an HTTP server. 
The DHCP server provides the option for clients to claim an IP address and release it when no longer needed. 
The DNS server enables clients to send DNS queries and receive responses. 
Lastly, the HTTP server is designed to redirect clients to a specific image through a URL.
The combination of these servers enables clients to easily connect to the network and access resources, 
including web pages and other digital content. 
The DHCP server assigns IP addresses dynamically, ensuring efficient use of available resources, 
while the DNS server simplifies the process of locating resources by mapping human-readable domain names to IP addresses. 
The HTTP server redirects clients to the desired image, enabling easy access to digital content.
Overall, this project aims to provide a comprehensive networking solution that simplifies the process of connecting to 
the network and accessing resources.
This project contains 3 types of application layer servers:
- DHCP server
- DNS server
- HTTP server

### DHCP Server
This is an implementation of a DHCP server in Python. 
DHCP is a protocol used to assign IP addresses and other network configuration parameters to devices on a network. 
This server can assign IP addresses dynamically to devices on a network based on requests received from DHCP clients.

#### Requirements

- Python 3.x 
- socket module 
- struct module 
- random module 
- binascii module

#### Usage
To use this DHCP server, simply run the dhcp_server.py file. 
The server will listen for DHCP Discovery and DHCP Request messages on port 67, 
and respond with DHCP Offer and DHCP ACK messages, respectively.

You can customize the server configuration by modifying the following variables in the dhcp_server.py file:
- `SERVER_IP`: The IP address of the DHCP server
- `SUBNET_MASK`: The subnet mask for the network
- `ROUTER_IP`: The IP address of the default gateway/router for the network
- `DNS_SERVER_IP`: The IP address of the DNS server for the network
- `LEASE`: The lease time for assigned IP addresses, in seconds
- `available_addresses`: A list of available IP addresses that can be assigned by the server
Note that the server will only assign IP addresses from the available_addresses list, so be sure to update this list with the desired IP address range for your network.

### DNS Server
This is a DNS server written in Python that can handle DNS queries and respond with an IP address for a given hostname.

#### Requirements
- Python 3.x 
- socket module 
- struct module 
- time module 
- sys module

#### Usage

To start the DNS server, run the following command in a terminal:
```sh
  sudo python3 dns_server.py
  ```
This will start the server on the default DNS port (53) and listen for incoming DNS queries.
By default, the server will use a hard-coded IP address (127.0.0.1).

### HTTP Server
This is a simple web server implemented in Python using socket programming. 
It handles with HTTP GET requests from client and respond with either an HTML file or an 
image file. The server contain the html file and send it to the client while receiving an HTML 
response, but this server don't have the png image file that needed for html file so while receiving png 
image file request the server redirect the client to another server (the image server) for downloading the image.
#### Dependencies
- Python 3.x
- socket library
- threading library 

#### How it Works
The server uses the socket library to create a socket object that listens for incoming packets on a specific IP address 
and port number. 
When a client sends an HTTP GET request to the server, the server uses the threading library to create a new thread to 
handle the client request. 
The thread reads the request, processes it, and sends a response back to the client. 
If the client requests an HTML file, the server reads the file from disk and sends it back to the client. 
If the client requests an image file, the server sends a redirection message to the client with the address of another server that contains the image file.

### HTTP Image Server

This is a simple server written in Python that serves a single image file to clients using the HTTP protocol.

#### Dependencies
This code requires the following modules:

- socket: for socket programming
- threading: to create a new thread to handle each client request
- src.backend.HTTP_Docs.HTTP_Servers.image: a custom module that provides the image file to be served

#### Implementation

The server is implemented using a loop that listens for incoming connections and spawns a new thread to handle each client request. 
The client_handler function handles the communication with the client, receiving the request and sending the response.
The image file is read from disk and sent to the client in chunks of 1024 bytes, using the sendall() method of the client socket.

### HTTP Client

This Python script provides a simple client that connects to a server to download an HTML file and an image file.

#### How it works
The client uses socket programming to establish a connection with the server and send HTTP requests. 
Specifically, it sends two requests:

An HTTP GET request for the HTML file:
```vbnet 
GET / HTTP/1.1
Host: 127:0:0:1
Accept: text/html,application/xhtml+xml
Connection: keep-alive
```

If the server responds with a status of HTTP/1.1 200 OK (text/html), the client extracts the HTML content from the response and saves it to a new file named new_html.html. It then opens this file in a web browser and sends a request for the image file.
An HTTP GET request for the image file:
```vbnet
GET /imgs/OurImage.png HTTP/1.1
Host: 127:0:0:1
Accept: image/webp,*/*
Connection: keep-alive
```
If the server responds with a status of HTTP/1.1 200 OK (JPEG JFIF image), 
the client extracts the image content from the response and saves it to a new file named 
OurImage.png.
If the server responds with a status of HTTP/1.1 301 Moved Permanently, 
it means that the image file is located on a different server. 
The client extracts the new server's IP address and port from the response and 
establishes a new connection with the new server to download the image file.

### GUI

### Unit-testing

## Sequence Diagram

## Hierarchy

## Links
